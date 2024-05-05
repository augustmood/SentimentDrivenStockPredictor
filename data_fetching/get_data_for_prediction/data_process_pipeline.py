import boto3
import os

def download_s3_bucket(bucket_name, local_directory):
    """
    Download the contents of an entire S3 bucket to a local directory.
    
    :param bucket_name: The name of the S3 bucket.
    :param local_directory: The local directory to which the bucket's contents will be downloaded.
    """
    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')
    for result in paginator.paginate(Bucket=bucket_name):
        if "Contents" in result:
            for obj in result['Contents']:
                # Define the local file path where the file will be saved
                local_file_path = os.path.join(local_directory, obj['Key'])
                # Ensure the local directory structure exists
                local_file_directory = os.path.dirname(local_file_path)
                if not os.path.exists(local_file_directory):
                    os.makedirs(local_file_directory)
                # Download the file from S3 to the specified local path
                s3.download_file(bucket_name, obj['Key'], local_file_path)
                print(f"Downloaded {obj['Key']} to {local_file_path}")

# Example usage
bucket_name = '733-project-new-data'
local_directory = './input_data/'
download_s3_bucket(bucket_name, local_directory)

from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, concat
import findspark
import logging
import time
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, concat_ws, lit, expr, greatest
import pandas as pd
import glob
import os

findspark.init()

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_time_taken(start, operation):
    end = time.time()
    logger.info(f"{operation} completed in {end - start:.2f} seconds")

# Start timing and log the initialization of the Spark session
logger.info("Initializing Spark session with optimized memory settings")
start_time = time.time()
spark = SparkSession.builder \
    .appName("Reddit Comment Context Builder") \
    .master("local[*]")  \
    .config("spark.executor.memory", "64g")  \
    .config("spark.driver.memory", "32g")  \
    .config("spark.executor.memoryOverhead", "4096") \
    .config("spark.driver.memoryOverhead", "2048")  \
    .config("spark.driver.maxResultSize", "8g") \
    .config("spark.driver.extraClassPath", "/Volumes/LaCie/wsb_archive/postgresql-42.7.3.jar") \
    .config("spark.driver.extraJavaOptions", "-XX:+UseG1GC") \
    .config("spark.executor.extraJavaOptions", "-XX:+UseG1GC") \
    .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:5.3.2")\
    .getOrCreate()
log_time_taken(start_time, "SparkSession initialization")


def process_files(csv_folder, column_selection, column_rename, output_file):
    """
    Processes CSV files from a specified folder into a single DataFrame, 
    selects specific columns, renames them, and writes to a parquet file.

    Parameters:
    - csv_folder: Folder path containing CSV files.
    - column_selection: List of columns to select from the DataFrame.
    - column_rename: Dictionary mapping original column names to new names.
    - output_file: Path to the output parquet file.
    """
    # Generate file path pattern
    file_pattern = f'{csv_folder}/*.csv'
    
    # Get a list of all CSV files in the specified folder
    csv_files = glob.glob(file_pattern)

    # Read CSV files and append to a list of DataFrames
    dataframes = [pd.read_csv(file) for file in csv_files]

    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Select and rename specified columns
    combined_df = combined_df[column_selection].rename(columns=column_rename)
    
    # Write to a parquet file
    combined_df.to_parquet(output_file)

def build_context_chain(comments: DataFrame, submissions: DataFrame, max_depth: int = None) -> DataFrame:
    # Alias submissions and comments with unique column names
    submissions_kv = submissions.select(
        expr("submission_id as s_key"),
        concat_ws(" ", col("title"), col("self_text")).alias("s_value")
    )

    # Including submission_id in the comments_kv DataFrame and introducing the reached_top flag
    comments_kv = comments.select(
        expr("comment_id as c_key"),
        col("parent_id").alias("c_parent_id"),
        col("comment_body").alias("c_value"),
        lit(False).alias("reached_top"),  # Initial reached_top flag set to False
    ).withColumn("curr_parent_id", col("c_parent_id"))  # Initialize curr_parent_id

    # Initialize context with the comment itself
    context_df = comments_kv.withColumn("context", col("c_value"))

    # Repartition DataFrames to optimize join performance
    submissions_kv = submissions_kv.repartition(200)
    comments_kv = comments_kv.repartition(200)
    context_df = context_df.repartition(200)
    i = 1
    while True and (max_depth is None or i <= max_depth):
        comments_iter = comments_kv.alias(f"c{i}")
        
        context_df = context_df.join(
            comments_iter,
            context_df["curr_parent_id"] == expr(f"concat('t1_', c{i}.c_key)"),
            "left_outer"
        ).join(
            submissions_kv,
            context_df["curr_parent_id"] == expr(f"concat('t3_', s_key)"),
            "left_outer"
        ).select(
            context_df["c_key"],
            when(
                context_df["curr_parent_id"].startswith("t3_"), 
                concat_ws(" |->| ", context_df["context"], submissions_kv["s_value"])
            ).when(
               col(f"c{i}.c_parent_id").isNull(),
                concat_ws(" |->| ", context_df["context"], lit("..."))
            ).when(
                context_df["curr_parent_id"].startswith("t1_"), 
                concat_ws(" |->| ", context_df["context"], col(f"c{i}.c_value"))
            ).otherwise(context_df["context"]).alias("context"),
            # Update curr_parent_id based on the join result
            when(context_df["curr_parent_id"].startswith("t1_"), col(f"c{i}.c_parent_id")).otherwise(context_df["curr_parent_id"]).alias("curr_parent_id"),
            # Update reached_top flag
            when(context_df["curr_parent_id"].isNull(), lit(True)).
            when(context_df["curr_parent_id"].startswith("t3_"), lit(True))
            .when(col(f"c{i}.curr_parent_id").isNull(), lit(True))
            .otherwise(context_df["reached_top"])
            .alias("reached_top")
        )
        # Check if all rows have reached the top; if so, break the loop
        if context_df.filter(col("reached_top") == False).count() == 0:
            break

        i += 1
    # Final join with original comments DataFrame to include additional details
    final_df = comments.join(
        context_df,
        comments["comment_id"] == context_df["c_key"],
        "left_outer"
    ).select(
        comments["datetime_utc"], comments["comment_id"], comments["submission_id"], 
        comments["parent_id"], comments["comment_score"], comments["comment_body"], 
        context_df["curr_parent_id"],
        context_df["context"].alias("comment_context"), context_df["reached_top"]
    )

    final_df = final_df.dropna(subset=["datetime_utc"]).dropDuplicates(['comment_id'])
    final_df = final_df.orderBy("datetime_utc", ascending=True)
    final_df.write.mode("overwrite").parquet("./sentiment_temp/wsb_comments_with_context")

    return final_df


# Define the column selection and renaming for comments
comments_columns = ['Datetime', 'Body', 'ID', 'Parent ID', 'Submission ID', 'Score']
comments_rename = {
    'Datetime': 'datetime_utc',
    'Body': 'comment_body',
    'ID': 'comment_id',
    'Parent ID': 'parent_id',
    'Submission ID': 'submission_id',
    'Score': 'comment_score'
}

# Define the column selection and renaming for submissions
submissions_columns = ['Datetime', 'Title', 'Body', 'ID', 'Score']
submissions_rename = {
    'Datetime': 'datetime_utc',
    'Title': 'title',
    'Body': 'self_text',
    'ID': 'submission_id',
    'Score': 'submission_score'
}

if not os.path.exists('temp'):
    # If the directory does not exist, create it
    os.makedirs('temp')
if not os.path.exists('sentiment_temp'):
    # If the directory does not exist, create it
    os.makedirs('sentiment_temp')
# Process comments CSV files
process_files('./input_data/wsb-comments', comments_columns, comments_rename, './temp/new_comments.parquet')
# Process submissions CSV files
process_files('./input_data/wsb-submissions', submissions_columns, submissions_rename, './temp/new_submissions.parquet')
new_comments = spark.read.parquet("./temp/new_comments.parquet")
new_submissions = spark.read.parquet("./temp/new_submissions.parquet")
build_context_chain(new_comments, new_submissions, 5)

import findspark
import logging
import time
import re
import os
import shutil
import yfinance as yf
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, explode, when, size, avg
from sparknlp.base import *
from sparknlp.annotator import *
from sparknlp.pretrained import PretrainedPipeline

findspark.init()
# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
start_time = time.time()
def log_time_taken(start, operation):
    end = time.time()
    logger.info(f"{operation} completed in {end - start:.2f} seconds")

# Define the class for simplifying company names
class CompanyNameSimplifier:
    def __init__(self):
        self.suffixes = [
            'Inc.', 'Inc', 'Corporation', 'Corp.', 'Corp', 'Company', 'Co.', 'Co', 
            'Limited', 'Ltd.', 'Ltd', 'PLC', 'NV', 'SA', 'AG', 'LLC', 'L.P.', 'LP'
        ]
        self.web_domains_regex = r'\.com|\.org|\.net|\.io|\.co|\.ai'

    def simplify_company_name(self, name):
        name = re.sub(self.web_domains_regex, '', name, flags=re.IGNORECASE)
        for suffix in self.suffixes:
            if name.endswith(suffix):
                name = name.replace(suffix, '')
                break
        name = re.split(',| -', name)[0]
        name = name.strip()
        return name

    def get_simplified_company_name(self, ticker):
        company = yf.Ticker(ticker)
        company_info = company.info
        full_name = company_info.get('longName', '')
        simple_name = self.simplify_company_name(full_name)
        return simple_name

class StockCommentsFilter:
    def __init__(self, ticker):
        self.ticker = ticker
        self.wsb_comments_with_context = spark.read.parquet("./sentiment_temp/wsb_comments_with_context")

    def filter_comments_by_ticker(self):
        simplifier = CompanyNameSimplifier()
        # Obtain the simplified company name for the given ticker
        company_name = simplifier.get_simplified_company_name(self.ticker)
        
        # Convert the ticker and company name to lowercase for a case-insensitive search
        ticker_lower = self.ticker.lower()
        company_name_lower = company_name.lower()

        # Filter the DataFrame for rows where the `comment_context` contains the ticker or the company name
        # Uses `lower` function to ensure that the search is case-insensitive
        filtered_df = self.wsb_comments_with_context.filter(
            lower(col("comment_context")).contains(ticker_lower) | 
            lower(col("comment_context")).contains(company_name_lower)
        ).select("datetime_utc", "comment_score", "comment_body")
        filtered_df.write.mode('overwrite').parquet(f'./sentiment_temp/stock_comments/{self.ticker}_comments')
        return filtered_df

class SentimentAnalyzer:
    def __init__(self, ticker):
        self.ticker = ticker
        self.pipeline = PretrainedPipeline('analyze_sentiment', lang='en')
        self.spark = spark

    def analyze(self):
        df = self.spark.read.parquet(f"./sentiment_temp/stock_comments/{self.ticker}_comments")
        df_renamed = df.withColumnRenamed("comment_body", "text")
        result = self.pipeline.transform(df_renamed)

        stock_sentiment = result.select(
            col("datetime_utc"),
            col("comment_score"),
            col("text").alias("comment_body"),
            col("sentiment.result").alias("comment_sentiment")
        )

        filtered_df = stock_sentiment.filter(size(col("comment_sentiment")) > 0)
        exploded_df = filtered_df.withColumn("individual_sentiment", explode(col("comment_sentiment")))

        scored_df = exploded_df.withColumn("sentiment_score",
                                           when(col("individual_sentiment") == "positive", 1)
                                           .when(col("individual_sentiment") == "negative", -1)
                                           .otherwise(0))

        stock_sentiment = scored_df.groupBy("datetime_utc", "comment_score", "comment_body").agg(avg("sentiment_score").alias("sentiment_score"))
        stock_sentiment = stock_sentiment.orderBy("datetime_utc")
        stock_sentiment.write.mode('overwrite').parquet(f"./sentiment_temp/stock_sentiments/{self.ticker}_sentiment")
        return stock_sentiment

class PopularityCalculator:
    def __init__(self, ticker, df, simplifier):
        self.ticker = ticker
        self.df = df
        self.simplifier = simplifier

    def calculate_popularity(self):
        # Convert to Eastern Time and simplify the company name
        df = self.df.withColumn("datetime_et", F.expr("from_utc_timestamp(datetime_utc, 'America/New_York')"))
        simplified_name = self.simplifier.get_simplified_company_name(self.ticker).lower()

        # Filter comments by ticker or company name
        filtered_comments = df.filter(
            lower(col("comment_context")).contains(self.ticker.lower()) |
            lower(col("comment_context")).contains(simplified_name)
        )

        # Aggregate daily mentions and total comments
        ticker_mentions = filtered_comments.groupBy(F.to_date("datetime_et").alias("date")).count().withColumnRenamed("count", "ticker_mentions")
        total_comments = df.groupBy(F.to_date("datetime_et").alias("date")).count().withColumnRenamed("count", "total_comments")

        # Calculate popularity percentage and sort by date
        popularity = ticker_mentions.join(total_comments, on="date") \
            .withColumn("popularity_percentage", F.col("ticker_mentions") / F.col("total_comments") * 100) \
            .orderBy("date")

        # Save the result
        save_path = f'./sentiment_temp/stock_popularity/{self.ticker}_popularity'
        popularity.write.mode('overwrite').parquet(save_path)

        return popularity


class StockSentimentPercentageAnalyzer:
    def __init__(self, ticker):
        self.ticker = ticker
        self.df = spark.read.parquet(f'./sentiment_temp/stock_sentiments/{ticker}_sentiment')

    def categorize_sentiment(self):
        df_with_sentiment_category = self.df.withColumn(
            "sentiment_category",
            when(self.df.sentiment_score > 0.05, "positive")
            .when(self.df.sentiment_score < -0.05, "negative")
            .otherwise("neutral")
        )
        return df_with_sentiment_category

    def analyze_sentiment(self):
        df = self.categorize_sentiment()
        df = df.withColumn("datetime_et", F.expr("from_utc_timestamp(datetime_utc, 'America/New_York')"))
        df = df.withColumn("date", F.to_date("datetime_et"))

        result = df.groupBy("date").agg(
            F.expr("count(1) as total_mentions"),
            F.sum(F.when(F.col("sentiment_category") == "positive", 1).otherwise(0)).alias("positive_count"),
            F.sum(F.when(F.col("sentiment_category") == "neutral", 1).otherwise(0)).alias("neutral_count"),
            F.sum(F.when(F.col("sentiment_category") == "negative", 1).otherwise(0)).alias("negative_count")
        ).withColumn(
            "positive_percentage", F.col("positive_count") / F.col("total_mentions") * 100
        ).withColumn(
            "neutral_percentage", F.col("neutral_count") / F.col("total_mentions") * 100
        ).withColumn(
            "negative_percentage", F.col("negative_count") / F.col("total_mentions") * 100
        )

        result = result.orderBy("date")
        result.write.mode('overwrite').parquet(f"./sentiment_temp/stock_sentiments_percentage/{self.ticker}_sentiment_percentage")
        return result

class StockDataMerger:
    def __init__(self, ticker):
        self.ticker = ticker
        self.spark = spark

    def merge_data(self):
        # Read stock popularity and sentiment percentage data
        stock_popularity = self.spark.read.parquet(f"./sentiment_temp/stock_popularity/{self.ticker}_popularity")
        stock_sentiment_percentage = self.spark.read.parquet(f"./sentiment_temp/stock_sentiments_percentage/{self.ticker}_sentiment_percentage")

        # Inner join on date
        stock_sentiment_and_popularity = stock_popularity.join(stock_sentiment_percentage, "date", "inner")

        # Selecting and renaming the desired columns
        stock_sentiment_and_popularity = stock_sentiment_and_popularity.select(
            col("date"),
            col("total_mentions").alias("mentions"),
            col("popularity_percentage").alias("popularity"),
            col("positive_percentage").alias("positive"),
            col("neutral_percentage").alias("neutral"),
            col("negative_percentage").alias("negative")
        )
        # Add a new column with the ticker
        stock_sentiment_and_popularity = stock_sentiment_and_popularity.withColumn('ticker', F.lit(self.ticker))

        stock_sentiment_and_popularity.write.mode('overwrite').parquet(f"./temp/stock_sentiment_and_popularity/{self.ticker}_sentiment_and_popularity")
        return stock_sentiment_and_popularity

def run_pipeline(ticker):
    # Step 01: Filter comments by ticker
    stock_filter = StockCommentsFilter(ticker)
    stock_filter.filter_comments_by_ticker()

    # # Step 02: Analyze sentiment
    analyzer = SentimentAnalyzer(ticker)
    analyzer.analyze()

    # # Step 03: Calculate popularity
    df = spark.read.parquet("./sentiment_temp/wsb_comments_with_context")
    simplifier = CompanyNameSimplifier()
    popularity_calculator = PopularityCalculator(ticker, df, simplifier)
    popularity_calculator.calculate_popularity()

    # Step 04: Calculate sentiment percentage
    analyzer = StockSentimentPercentageAnalyzer(ticker)
    analyzer.analyze_sentiment()

    # Step 05: Merge popularity and sentiment percentage data
    merger = StockDataMerger(ticker)
    merger.merge_data()
    
    # Step 06: Show the merged data
    spark.read.parquet(f"./temp/stock_sentiment_and_popularity/{ticker}_sentiment_and_popularity").show()

def main():
    tickers = ["AAPL", "NVDA", "TSLA"]
    for ticker in tickers:
        run_pipeline(ticker)
    dir_path = "./sentiment_temp"
    if os.path.exists(dir_path):
        # Recursively delete the directory
        shutil.rmtree(dir_path)
        print(f"The directory '{dir_path}' has been deleted.")
    else:
        print(f"The directory '{dir_path}' does not exist.")

if __name__ == "__main__":
    main()

import pandas as pd
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def read_and_process_parquet(file_path: str) -> pd.DataFrame:
    df = pd.read_parquet(file_path)
    df = df.drop_duplicates(subset=['title', 'time_published', 'url'])
    df['date'] = pd.to_datetime(df['time_published']).dt.strftime('%Y-%m-%d')
    return df

def compute_priority_and_weighted_score(df: pd.DataFrame, priority_score: dict) -> pd.DataFrame:
    df_cp = df.copy()
    df_cp['priority'] = df_cp['source'].map(priority_score)
    df_cp['weighted_score'] = df_cp.overall_sentiment_score * df_cp.priority
    return df_cp

def calculate_daily_weighted_avg(df_cp: pd.DataFrame, company_name: str) -> pd.DataFrame:
    daily_weighted_avg = df_cp.groupby('date').apply(
        lambda x: (x['weighted_score'].sum() / x['priority'].sum()) if x['priority'].sum() != 0 else 0
    ).reset_index(name='daily_weighted_avg')
    daily_weighted_avg['ticker'] = company_name
    return daily_weighted_avg

def combine_daily_averages(*dfs) -> pd.DataFrame:
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df['date'] = pd.to_datetime(combined_df['date'], format='%Y-%m-%d')
    return combined_df

def process_ticker_data(ticker: str, priority_score: dict) -> pd.DataFrame:
    df = read_and_process_parquet(f'./input_data/stock-news/{ticker}_news.parquet')
    df_cp = compute_priority_and_weighted_score(df, priority_score)
    daily_weighted_avg = calculate_daily_weighted_avg(df_cp, ticker)
    return daily_weighted_avg

def get_combined_stock_price_data(tickers):
    # Calculate dates for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=500)

    # Format dates in YYYY-MM-DD format
    end_date = end_date.strftime('%Y-%m-%d')
    start_date = start_date.strftime('%Y-%m-%d')

    # DataFrame to store combined stock data
    combined_data = pd.DataFrame()

    for ticker in tickers:
        # Fetch stock data
        data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
        # Add a 'Ticker' column
        data['ticker'] = ticker
        # Reset the index to make 'Date' a column
        data = data.reset_index()
        # Rename 'Date' column to 'date'
        data = data.rename(columns={'Date': 'date'})
        # Append to the combined DataFrame
        combined_data = pd.concat([combined_data, data])

    return combined_data

def main():
    # Priority score dictionary is defined only once
    priority_score = {
        'The Week News': 1,
        'Wall Street Journal': 4,
        'GlobeNewswire': 1,
        'Zacks Commentary': 1,
        'Reuters': 4,
        'CNBC': 1,
        'The Atlantic': 1,
        'New York Times': 4.5,
        'Decrypt.co': 1,
        'Investing News Network': 1,
        'Investors Business Daily': 1,
        'The Block Crypto': 1,
        'StockMarket.com': 1,
        'Forbes': 3.5,
        'Fox Business News': 1,
        'The Financial Express': 1,
        'Motley Fool': 1,
        'Cointelegraph': 1,
        'PennyStocks.com': 1,
        'The Street': 1,
        'Economic Times': 1,
        'Money Control': 1,
        'Al Jareeza': 1,
        'Benzinga': 1,
        'Axios': 1,
        'MarketWatch': 1,
        'CNN': 4,
        'Stocknews.com': 1,
        'The Economist': 4,
        'Money Morning': 1,
        'Kiplinger': 1,
        'Associated Press': 4.5,
        'Barrons': 1,
        'Financial News London': 1,
        'FinancialBuzz': 1,
        'Fast Company': 1,
        'Financial Times': 4,
        'Business Standard': 1,
        'UPI Business': 1,
        'South China Morning Post': 3.5,
        'Business Insider': 1,
        'Investor Ideas': 1,
        'Canada Newswire': 1,
        'PR Newswire': 1
    }
    
    tickers = ['AAPL', 'NVDA', 'TSLA']
    daily_weighted_avgs = [process_ticker_data(ticker, priority_score) for ticker in tickers]
    
    combined_daily_averages = combine_daily_averages(*daily_weighted_avgs)
    combined_stock_price = get_combined_stock_price_data(tickers)
    combined_stock_data = pd.merge(combined_stock_price, combined_daily_averages, on=['date', 'ticker'], how='left')
    combined_stock_data = combined_stock_data.groupby('ticker', group_keys=False).apply(lambda group: group.fillna(method='ffill'))
    combined_stock_data = combined_stock_data.groupby('ticker', group_keys=False).apply(lambda group: group.fillna(method='bfill'))  
    combined_stock_data.to_csv('./temp/stock_news_combined.csv', index=False)
    return combined_stock_data

if __name__ == "__main__":
    main()

import pandas as pd
import os

class StockDataProcessor:
    def __init__(self, stock_data_file):
        self.stock_data_file = stock_data_file
        self.df = None
        self.combined_df = None

    def load_stock_data(self):
        self.df = pd.read_csv(self.stock_data_file)
        self.df = self.df.rename(columns={'Date': 'date', 'company_name': 'ticker'})
        self.df['date'] = pd.to_datetime(self.df['date'], format='%Y-%m-%d')

    def generate_sentiment_file_names(self, tickers):
        """Generates file paths for sentiment data based on ticker symbols."""
        return [f'./temp/stock_sentiment_and_popularity/{ticker}_sentiment_and_popularity' for ticker in tickers]

    def load_and_combine_sentiment_data(self, tickers):
        files = self.generate_sentiment_file_names(tickers)
        dfs = []
        for file in files:
            temp_df = pd.read_parquet(file)
            dfs.append(temp_df)

        self.combined_df = pd.concat(dfs, ignore_index=True)
        self.combined_df['date'] = pd.to_datetime(self.combined_df['date'], format='%Y-%m-%d')

    def merge_dataframes(self):
        self.combined_df = pd.merge(self.df, self.combined_df, on=['date', 'ticker'], how='left')

# Usage
if __name__ == "__main__":
    stock_data_processor = StockDataProcessor('./temp/stock_news_combined.csv')
    stock_data_processor.load_stock_data()
    tickers = ['AAPL', 'NVDA', 'TSLA']  # Now you can just list your tickers here
    stock_data_processor.load_and_combine_sentiment_data(tickers)
    stock_data_processor.merge_dataframes()
    directory_path = 'result'
    # Check if the directory exists
    if not os.path.exists(directory_path):
        # If the directory does not exist, create it
        os.makedirs(directory_path)
    new_data_for_prediction = stock_data_processor.combined_df.dropna(subset=['mentions'])
    cols = list(new_data_for_prediction.columns)
    cols.insert(len(cols), cols.pop(cols.index('daily_weighted_avg')))
    new_data_for_prediction = new_data_for_prediction.loc[:, cols]
    new_data_for_prediction.to_csv('./data_for_prediction/new_data_for_prediction.csv', index=False)

import os
import boto3
import os

def upload_folder_to_s3(bucket_name, folder_path, s3_folder):
    """
    Upload a folder to an S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :param folder_path: Local path to the folder to upload.
    :param s3_folder: S3 folder path where files will be uploaded.
    """
    try:
        s3 = boto3.client('s3')

        for subdir, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(subdir, file)
                with open(full_path, 'rb') as data:
                    file_path_on_s3 = os.path.join(s3_folder, os.path.relpath(full_path, folder_path))
                    s3.upload_fileobj(data, bucket_name, file_path_on_s3)
                    print(f"File {file} uploaded to {file_path_on_s3}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
bucket_name = '733-project-new-data'
local_folder_path = './data_for_prediction/'
s3_folder_path = 'data_for_prediction'

upload_folder_to_s3(bucket_name, local_folder_path, s3_folder_path)

# Delete the temp directory and all its contents
temp_directory = './temp'
shutil.rmtree(temp_directory)
