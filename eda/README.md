# Stock Data EDA and ML Model Testing

This project focuses on exploratory data analysis (EDA) of stock market data, including data collection, data analysis, and testing machine learning (ML) models.

## Overview

This repository contains a collection of Jupyter notebooks and datasets for analyzing stock market data. The primary goal of this project is to provide insights into stock market trends and to evaluate the performance of machine learning models for predicting stock prices.

## Data Collection

The stock market data used in this project is collected from various sources, including financial APIs and public datasets. We leverage APIs such as Yahoo Finance and Alpha Vantage to gather historical stock price data, as well as  sentiment data from sources like Reddit and stock market news.

## Data Analysis

The data analysis process involves exploring the collected stock market data to identify patterns, correlations, and anomalies. The Jupyter notebooks in the `notebooks` directory provide detailed analyses of various aspects of the stock market, including price trends, trading volumes, and sentiment analysis of news articles.

## Machine Learning Model Testing

In this section, we evaluate the performance of machine learning models for predicting stock prices. We use historical stock market data as features to train and test regression models such as linear regression, but we decided to use LSTM and it has better performance.

## Folder Structure

```
.
└── cmpt-733-final-project-eda
    ├── additional-data/                                <- additional data files for data analysis
    │   ├── all-states-history.csv
    │   └── national-history.csv
    ├── config/                                         <- main config
    │   └── config.yaml
    ├── covid-data-analysis/                            <- covid data collection and analysis
    │   ├── covid_data_analysis.ipynb
    │   └── na_covid_data_merged.csv
    ├── gdp-rate-analysis/                              <- GDP data collection and analysis
    │   ├── gdp_data.csv
    │   └── gdp_data_analysis.ipynb
    ├── inflation-rate-analysis/                        <- inflation data collection and analysis
    │   ├── inflation_data.csv
    │   └── inflation_data_analysis.ipynb
    ├── ml-models-test-notebook/                        <- tried a couple of ML modelss
    │   ├── gpr_model_analysis.ipynb
    │   └── stock_and_epidemic.ipynb
    ├── reddit-sentimental-analysis/                    <- reddit comments data collection and analysis
    │   ├── comments/...
    │   ├── fetch_test_code/...
    │   ├── posts/...
    │   ├── apify_reddit_scraper.ipynb
    │   ├── extract_comments.ipynb
    │   ├── extract_posts.ipynb
    │   ├── fetch_reddit_posts.py
    │   ├── reddit_comments_extractor.py
    │   ├── reddit_sentimental.ipynb
    │   ├── requirements.txt
    │   ├── temp.ipynb
    │   └── temp.py
    ├── stock-historical-data-analysis/                 <- stock historical data collection and analysis
    │   ├── amzn.csv
    │   ├── appl.csv
    │   ├── data_eda.ipynb
    │   ├── data_extractor.ipynb
    │   └── initial_exploration.ipynb
    ├── stock-news-sentimental-analysis/                <- stock news data collection and analysis
    │   ├── apple_new.parquet
    │   ├── data.csv
    │   ├── eda_news_data.ipynb
    │   ├── nvidia_news.parquet
    │   ├── stock_data.csv
    │   ├── stock_news_extractor.ipynb
    │   ├── stock_news.csv
    │   └── tesla_news.parquet
    ├── wsb-analysis/                                   <- WallStreetBets analysis
    │   ├── analysis_stage_01.ipynb
    │   ├── context_build.ipynb
    │   ├── nlp_sentiment_pipeline.ipynb
    │   └── spark_nlp_analysis.ipynb
    ├── wsb-data-engineering/                           <- WallStreetBets data engineering
    │   ├── wallstreetbets_comment_loader.py
    │   └── wallstreetbets_submission_loader.py
    ├── requirements.txt                                <- requirements to be installed
    ├── README.md                                       <- deployment & launch instruction
    └── .gitignore
```


## Dependencies installment

To set up the project environment

```bash
python -m pip install -r requirements.txt
