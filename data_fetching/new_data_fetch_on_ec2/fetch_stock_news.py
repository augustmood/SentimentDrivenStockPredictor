import requests
import pandas as pd
from datetime import datetime, timedelta
import logging

# Setup basic configuration for logging
logging.basicConfig(filename='stock_news_fetch_history.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def append_to_parquet_file(new_df, filename):
    try:
        # Attempt to read the existing data
        existing_df = pd.read_parquet(filename)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        logging.info(f"Appended new data to {filename}")
    except FileNotFoundError:
        # If the file does not exist, create a new one from the new data
        updated_df = new_df
        logging.info(f"Created new file {filename} as it did not exist.")
    # Save the updated DataFrame
    updated_df.to_parquet(filename)

time_from = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

urls_to_filenames = {
    f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&time_from={time_from}T0130&limit=1000&sort=EARLIEST&apikey=U0UD1WX9BNOZHJS7': './stock-news/AAPL_news.parquet',
    f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=NVDA&time_from={time_from}T0130&limit=1000&sort=EARLIEST&apikey=U0UD1WX9BNOZHJS7': './stock-news/NVDA_news.parquet',
    f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=TSLA&time_from={time_from}T0130&limit=1000&sort=EARLIEST&apikey=U0UD1WX9BNOZHJS7': './stock-news/TSLA_news.parquet'
}

for url, output_filename in urls_to_filenames.items():
    try:
        r = requests.get(url)
        data = r.json()

        if 'feed' in data:
            df = pd.DataFrame(data['feed'])
            append_to_parquet_file(df, output_filename)
        else:
            logging.warning(f"The 'feed' key was not found in the data for {output_filename}")
    except Exception as e:
        logging.error(f"Error processing {output_filename}: {str(e)}")
