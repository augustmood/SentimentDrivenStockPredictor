import requests
import pandas as pd
from datetime import datetime, timedelta

def append_to_parquet_file(new_df, filename):
    try:
        existing_df = pd.read_parquet(filename)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    except FileNotFoundError:
        updated_df = new_df

    updated_df.to_parquet(filename)

time_from = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

# URLs mapped
urls_to_filenames = {
    f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&time_from={time_from}T0001&limit=1000&sort=EARLIEST&apikey=U0UD1WX9BNOZHJS7': './apple_news.parquet',
    f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=NVDA&time_from={time_from}T0001&limit=1000&sort=EARLIEST&apikey=U0UD1WX9BNOZHJS7': './nvidia_news.parquet',
    f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=TSLA&time_from={time_from}T0001&limit=1000&sort=EARLIEST&apikey=U0UD1WX9BNOZHJS7': './tesla_news.parquet'
}

for url, output_filename in urls_to_filenames.items():
    r = requests.get(url)
    data = r.json()

    if 'feed' in data:
        df = pd.DataFrame(data['feed'])
        # print(df)
        append_to_parquet_file(df, output_filename)
    else:
        print(f"The 'feed' key was not found in the data for {output_filename}")
