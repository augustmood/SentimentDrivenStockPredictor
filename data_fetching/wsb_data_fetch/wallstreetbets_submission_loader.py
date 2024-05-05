import pandas as pd
import zstandard as zstd
import simplejson as json
import io
from sqlalchemy import create_engine
import logging

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, filepath, limit=None):
        self.filepath = filepath
        self.limit = limit

    def read_zst_to_dataframe(self):
        logger.info(f"Starting to process file: {self.filepath}")
        dctx = zstd.ZstdDecompressor()
        rows = []
        with open(self.filepath, 'rb') as fh:
            with dctx.stream_reader(fh) as reader:
                text_stream = io.TextIOWrapper(reader, encoding='utf-8')
                for line in text_stream:
                    if self.limit is not None and len(rows) >= self.limit:
                        break
                    row = json.loads(line)
                    rows.append(row)
        logger.info(f"Finished processing file: {self.filepath}")
        return pd.DataFrame(rows)

# CREATE TABLE wsb_submissions (
#     datetime_utc TIMESTAMP WITH TIME ZONE,
#     post_id VARCHAR(10) PRIMARY KEY,
#     url TEXT,
#     title TEXT,
#     self_text TEXT,
#     is_self BOOLEAN,
#     num_comments INT,
#     likes INT,
#     downs INT,
#     ups INT,
#     post_score INT,
#     distinguished TEXT,
#     edited BOOLEAN,
#     author TEXT,
#     over_18 BOOLEAN
# );

class DataTransformer:
    @staticmethod
    def refine_and_transform(df):
        logger.info("Transforming DataFrame")
        df['datetime_utc'] = pd.to_datetime(df['created_utc'], unit='s', utc=True)
        df.rename(columns={'selftext': 'self_text', 'score': 'post_score', 'id': 'post_id'}, inplace=True)
        final_columns = ['datetime_utc', 'post_id', 'url', 'title', 'self_text', 'is_self', 'num_comments', 'likes', 'downs', 'ups', 'post_score', 'distinguished', 'edited', 'author', 'over_18']
        # Convert each column to its correct data type
        df['is_self'] = df['is_self'].apply(lambda x: x if str(x).lower() in ['true', 'false'] else None)
        df['num_comments'] = pd.to_numeric(df['num_comments'], errors='coerce').astype('Int64')
        df['likes'] = pd.to_numeric(df['likes'], errors='coerce').astype('Int64')
        df['downs'] = pd.to_numeric(df['downs'], errors='coerce').astype('Int64')
        df['ups'] = pd.to_numeric(df['ups'], errors='coerce').astype('Int64')
        df['post_score'] = pd.to_numeric(df['post_score'], errors='coerce').astype('Int64')
        df['edited'] = df['edited'].apply(lambda x: x if str(x).lower() in ['true', 'false'] else None)
        df['over_18'] = df['over_18'].apply(lambda x: x if str(x).lower() in ['true', 'false'] else None)
        string_columns = ['url', 'title', 'self_text', 'distinguished', 'author']
        for col in string_columns:
            df[col] = df[col].apply(lambda x: x.replace('\x00', '\uFFFD') if isinstance(x, str) else x)

        # Get the number of rows before dropping duplicates
        rows_before = df.shape[0]
        # Drop duplicates based on the 'post_id' column
        df.drop_duplicates(subset=['post_id'], keep='last', inplace=True)
        # Get the number of rows after dropping duplicates
        rows_after = df.shape[0]
        # Calculate the number of rows dropped
        rows_dropped = rows_before - rows_after
        print(f"Number of duplicate rows dropped: {rows_dropped}")
        return df[final_columns].copy()

class DatabaseManager:
    def __init__(self, db_connection_string, table_name='wsb_submissions'):
        self.db_engine = create_engine(db_connection_string)
        self.table_name = table_name

    def load_to_database(self, df):
        logger.info("Loading data into the database")
        df.to_sql(self.table_name, self.db_engine, if_exists='append', index=False)
        logger.info("Data loading complete")

def process_file(filepath, db_connection_string, limit=None):
    loader = DataLoader(filepath, limit)
    df = loader.read_zst_to_dataframe()
    df = DataTransformer.refine_and_transform(df)
    db_manager = DatabaseManager(db_connection_string)
    db_manager.load_to_database(df)

def main():
    filepath = 'dataset/wallstreetbets_submissions.zst'
    db_connection_string = 'postgresql://postgres:trust@localhost:5432/wsb_database'
    process_file(filepath, db_connection_string)

if __name__ == "__main__":
    main()