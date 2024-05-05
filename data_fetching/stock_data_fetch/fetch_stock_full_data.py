import yfinance as yf
import pandas as pd
import datetime

def get_stock_data(tickers, start_date, end_date):
    dfs = []
    for ticker in tickers:
        # Download stock data
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        stock_data.reset_index(inplace=True)  # Reset index to turn the Date index into a column
        stock_data['Ticker'] = ticker  # Add a column for the ticker symbol
        dfs.append(stock_data)
    # Concatenate all dataframes and return
    all_data = pd.concat(dfs)
    # Rename columns
    all_data.rename(columns={'Date': 'date', 'Ticker': 'ticker'}, inplace=True)
    return all_data

tickers = ['AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN']  # Example list of tickers
start_date = '2012-01-01'
end_date = datetime.datetime.now().strftime('%Y-%m-%d')

stock_df = get_stock_data(tickers, start_date, end_date)
# Convert the DataFrame to JSON and save it
stock_df.to_json('stock_full_data.json', orient='records')


