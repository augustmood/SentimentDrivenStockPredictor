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
        total_rows_processed = 0  # Initialize a counter for the total number of rows processed

        with open(self.filepath, 'rb') as fh:
            with dctx.stream_reader(fh) as reader:
                text_stream = io.TextIOWrapper(reader, encoding='utf-8')
                chunk_size = 1024 * 1024  # Define a suitable chunk size
                
                while True:
                    # Adjust the chunk size if we are approaching the limit
                    if self.limit is not None and (total_rows_processed + chunk_size) > self.limit:
                        chunk_size = self.limit - total_rows_processed

                    rows = [json.loads(line) for line, _ in zip(text_stream, range(chunk_size))]
                    if not rows or (self.limit is not None and total_rows_processed >= self.limit):
                        break

                    total_rows_processed += len(rows)  # Update the total number of rows processed
                    
                    df = pd.DataFrame(rows)
                    yield df
                    
                    # If a limit is set and we've reached it, stop reading further
                    if self.limit is not None and total_rows_processed >= self.limit:
                        logger.info(f"Reached the limit of {self.limit} rows, stopping.")
                        break

        logger.info(f"Finished processing file: {self.filepath}")

# CREATE TABLE wsb_comments (
#     datetime_utc TIMESTAMP WITH TIME ZONE NOT NULL,
#     comment_id VARCHAR(20) PRIMARY KEY,
#     submission_id VARCHAR(20) NOT NULL,
#     parent_id VARCHAR(20) NULL, -- Can be NULL for top-level comments
#     distinguished TEXT NULL, -- Can be NULL if the comment is not distinguished
#     archived BOOLEAN NOT NULL,
#     edited BOOLEAN NOT NULL,
#     ups INT NOT NULL,
#     downs INT NOT NULL,
#     controversiality INT NOT NULL CHECK (controversiality IN (0, 1)),
#     comment_score INT NOT NULL,
#     comment_body TEXT NULL -- Can be NULL for deleted or removed comments
# );

# -- Indexes to improve query performance
# CREATE INDEX idx_submission_id ON wsb_comments (submission_id);
# CREATE INDEX idx_parent_id ON wsb_comments (parent_id);
        
class DataTransformer:
    @staticmethod
    def refine_and_transform(df):
        # Convert 'created_utc' to a readable datetime format
        df['datetime_utc'] = pd.to_datetime(df['created_utc'], unit='s', utc=True)
        
        # Map 'link_id' and 'id' to 'submission_id' and 'comment_id' respectively, as specified
        df.rename(columns={
            'id': 'comment_id',
            'link_id': 'submission_id',
            'score': 'comment_score',
            'body': 'comment_body'
        }, inplace=True)
        
        # Convert boolean columns from string to actual boolean values or None
        boolean_columns = ['archived', 'edited']
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: True if str(x).lower() == 'true' else (False if str(x).lower() == 'false' else None))
            else:
                df[col] = pd.Series([pd.NA] * len(df), index=df.index).astype('Int64')
                logger.warning(f"Column '{col}' is missing from the dataset, impacting all {len(df)} entries. This could influence subsequent data processing steps.")
        
        # Convert numeric columns and handle errors by coercing to NaN, then converting NaNs to a nullable integer type
        numeric_columns = ['ups', 'downs', 'controversiality', 'comment_score']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            else:
                df[col] = pd.Series([pd.NA] * len(df), index=df.index).astype('Int64')
                logger.warning(f"Column '{col}' is missing from the dataset, impacting all {len(df)} entries. This could influence subsequent data processing steps.")
        
        # Handle potentially nullable text columns and replace non-UTF characters
        text_columns = ['comment_body', 'distinguished']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.replace('\x00', '\uFFFD') if isinstance(x, str) else x)
            else:
                df[col] = pd.Series([pd.NA] * len(df), index=df.index)
                logger.warning(f"Column '{col}' is missing from the dataset, impacting all {len(df)} entries. This could influence subsequent data processing steps.")
        
        # Select and reorder the final set of columns as specified
        final_columns = ['datetime_utc', 'comment_id', 'submission_id', 'parent_id', 
                        'distinguished', 'archived', 'edited', 'ups', 'downs', 
                        'controversiality', 'comment_score', 'comment_body']
        
        # Drop duplicates based on the 'comment_id' column
        df.drop_duplicates(subset=['comment_id'], keep='last', inplace=True)

        return df[final_columns].copy()

class DatabaseManager:
    def __init__(self, db_connection_string, table_name='wsb_comments'):
        self.db_engine = create_engine(db_connection_string)
        self.table_name = table_name

    def load_to_database(self, df):
        logger.info("Loading data into the database")
        df.to_sql(self.table_name, self.db_engine, if_exists='append', index=False, method='multi')
        logger.info("Data loading complete")

def process_file(filepath, db_connection_string, limit=None):
    loader = DataLoader(filepath, limit)
    db_manager = DatabaseManager(db_connection_string)
    
    for chunk_df in loader.read_zst_to_dataframe():
        processed_df = DataTransformer.refine_and_transform(chunk_df)
        db_manager.load_to_database(processed_df)

def main():
    filepath = 'dataset/wallstreetbets_comments.zst'
    db_connection_string = 'postgresql://postgres:trust@localhost:5432/wsb_database'
    process_file(filepath, db_connection_string)

if __name__ == "__main__":
    main()