from django.http import HttpResponse, JsonResponse
from keras.models import load_model
import numpy as np
import pandas as pd
import yfinance as yf
from joblib import load
from datetime import datetime, timedelta
import os
import boto3

MODEL_DIR = './models'
SCALER_DIR = './models/scalers'


# Function to load models and scalers on demand
def load_resources(ticker):
    model_path = os.path.join(MODEL_DIR, f"{ticker.upper()}_model.keras")
    scaler_path = os.path.join(SCALER_DIR, f"{ticker.upper()}_scaler.joblib")

    model = load_model(model_path)
    scaler = load(scaler_path)

    return model, scaler


# Improved prediction function
def model_predict(input_data, model, scaler):
    # Ensure input_data is a numpy array
    input_data_np = input_data.values.reshape(1, -1)

    # Scale the input data
    scaled_input_data = scaler.transform(input_data_np).astype('float32')

    # Reshape the input data to match the model's expected input shape
    scaled_input_data = np.reshape(scaled_input_data, (1, 1, -1))

    # Make predictions
    predictions = model.predict(scaled_input_data)

    # Reshape predictions to match the scaler's expected input shape for inverse_transform
    predictions = np.reshape(predictions, (1, -1))

    # Apply inverse_transform to predictions
    prediction_copies_array = np.repeat(predictions, input_data_np.shape[1], axis=-1)
    original_scale_predictions = scaler.inverse_transform(prediction_copies_array)[:, 0]
    print(original_scale_predictions)
    return original_scale_predictions

def get_prediction_variables(input_data):
    # Define the mapping of DataFrame column names to the desired output format
    column_mapping = {
        'Open': "Open",
        'High': "High",
        'Low': "Low",
        'Close': "Close",
        'Adj Close': "Adj Close",
        'Volume': "Volume",
        'positive': "WSB Community Positive Sentiment",
        'negative': "WSB Community Negative Sentiment",
        'neutral': "WSB Community Neutral Sentiment",
        'mentions': "WSB Community Mentions",
        'popularity': "WSB Community Popularity",
        'daily_weighted_avg': "Stock News Sentiment Score",
    }

    # Initialize the list to store prediction variables
    prediction_variables = []

    # Iterate over the column_mapping to create the prediction_variables list
    for key, attribute in column_mapping.items():
        # Check if the key exists in the DataFrame to avoid KeyError
        if key in input_data.columns:
            # Special formatting for percentages
            if 'Score' in attribute:
                value = str(input_data[key].iloc[-1])  # Convert numerical values to string
            elif 'Sentiment' in attribute or 'Popularity' in attribute:
                value = f"{input_data[key].iloc[-1]}%"  # sentiment values are in decimal form
            else:
                value = str(input_data[key].iloc[-1])

            prediction_variables.append({"attribute": attribute, "value": value})

    return prediction_variables

def get_company_info(ticker_symbol):
    # Fetch the ticker data using yfinance
    ticker = yf.Ticker(ticker_symbol)

    # Attempt to fetch the info dictionary for the ticker
    info = ticker.info

    # Prepare the data in the desired format
    company_info = [
        {"attribute": "Name", "value": info.get('longName', 'N/A')},
        {"attribute": "Ticker", "value": ticker_symbol.upper()},
        {"attribute": "Industry", "value": info.get('industry', 'N/A')},
    ]

    return company_info

def load_data_for_prediction(ticker):
    try:
        # Create an S3 client
        s3 = boto3.client('s3')
        # The name of your S3 bucket
        bucket_name = '733-project-new-data'
        # The path to your file on S3
        s3_file_path = 'data_for_prediction/new_data_for_prediction.csv'
        # The path to where you want to download the file
        local_file_path = 'data/new_data.csv'
        # Download the file
        s3.download_file(bucket_name, s3_file_path, local_file_path)
        print("File downloaded successfully.")
    except Exception as e:
        # This block is executed if any error occurs in the try block
        print(f"Failed to download file: {e}. Will proceed using the existing local version of the file.")
    input_data = pd.read_csv('data/new_data.csv')
    input_data = input_data.sort_values(by="date").drop(["date", "ticker"], axis=1)[input_data["ticker"] == ticker].tail(1)
    return input_data

def load_data_for_graph(ticker, result):
    df = pd.read_csv('data/new_data.csv')
    df = df.sort_values(by="date")[df["ticker"] == ticker]
    df = df[["date", "Close", "ticker"]]
    new_row = {"date": datetime.now().strftime('%Y-%m-%d'), "Close": result, "ticker":ticker}
    new_row_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_row_df], ignore_index=True)
    return df.to_json(orient='records', lines=False)

def get_data_for_stock(request, ticker):  # Notice 'ticker' is now a parameter of the function
    try:
        model, scaler = load_resources(ticker.upper())
        input_data = load_data_for_prediction(ticker)
        predictions = model_predict(input_data, model, scaler)
        company_info = get_company_info(ticker.upper())
        prediction_variables = get_prediction_variables(input_data)
        plot_data = load_data_for_graph(ticker, str(predictions[0]))
        response_data = {
            "predictionResult": [{"attribute": "Predicted Price", "value": str(predictions[0])},
                                 {"attribute": "Date", "value": datetime.now().strftime('%Y-%m-%d')}],  # Ensure the value is a string or serializable type
            "companyInfo": company_info,
            "predictionVariables": prediction_variables,
            "plotData": plot_data
        }
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)