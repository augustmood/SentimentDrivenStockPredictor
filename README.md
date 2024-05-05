# CMPT-733-Project

## Description
This project is aimed at showcasing the end-to-end process of a typical data science project, including data fetching, exploratory data analysis (EDA), machine learning (ML) pipelines, and a web application for visualization of solutions.

## Project Structure
The project is organized into the following directories:

1. **EDA**: Contains notebooks/scripts for exploratory data analysis.
2. **ML Pipelines**: Contains scripts for building and deploying machine learning models.
3. **Data Fetching**: Contains scripts for fetching and preprocessing data.
4. **Web App**: Contains the backend and frontend code for the visualization web application.

## Repository Structure

```
.
├── README.md
├── data_fetching
│   ├── get_data_for_prediction/
│   ├── new_data_fetch_on_ec2/
│   ├── stock_data_fetch/
│   └── wsb_data_fetch/
├── eda/
├── ml_pipeline
│   ├── ml_pipeline.ipynb
│   └── model_and_scaler/
└── web_app
    ├── back_end/
    └── front_end/
```

## Usage
**EDA**
Explore the notebooks in the EDA directory to understand the data and gain insights.

**ML Pipelines**
Refer to the ML Pipelines directory for scripts related to training, evaluation, and deployment of machine learning models.

**Data Fetching**
Use the scripts in the Data Fetching directory to fetch and preprocess data for analysis.

**Web App**
The Web App directory contains the backend and frontend code for the visualization web application. Follow the instructions in the respective directories to set up and run the web application.

## Installation and Launch Instructions
### Prerequisites
Before you begin, ensure you have Docker and Docker Compose installed on your system. These tools are required to containerize the application and its services, making it easier to deploy and run on any system without worrying about dependencies.

### Getting Started
1. **Clone the Repository**

    Start by cloning the application repository to your local machine. Open a terminal and run the following command:

    ```
    git clone https://github.sfu.ca/bla175/cmpt-733-project.git
    ```

    or 

    ```
    git@github.sfu.ca:bla175/cmpt-733-project.git
    ```

2. **Navigate to the Application Directory**

    Change your current directory to the cloned repository where the docker-compose.yml file is located:

    ```
    cd web_app
    ```

3. **Launch the Application with Docker Compose**

    Use the following Docker Compose command to build and start the application in detached mode (running in the background):

    ```
    docker-compose up -d
    ```
    This command reads the `docker-compose.yml` file in the current directory, builds the necessary Docker images, and starts the services defined in the file.

### Accessing the Application
After launching the application with Docker Compose, you can access the various components of the application using the URLs provided below:

- Front-End Application: Navigate to http://127.0.0.1:3000/ in your web browser to access the front-end interface of the application.

- Additional Services: If your application includes other services that can be accessed via a web interface, you can access them at http://127.0.0.1:8080/.

### Logging In
Upon accessing the front-end application, if prompted for a login, the application is designed to automatically fill in the default credentials. However, if the username and password are not pre-loaded, you can manually enter the following default credentials:

- Username: admin
- Password: 123456

These credentials should grant you access to the application. If you encounter any issues or need further assistance, please refer to the application documentation or contact the support team.

## Tools/Technologies

* Data Fetch Automation: Amazon EC2
* ETL operations: Apache Spark, Pandas, PostgreSQL
* Deployment: Docker
* Visualization: Apache Echarts
* Backend: Django
* Frontend: Vue.js, Elment UI

## Contributors

* Binming Li
* Chengkun He
* Haimo Xu
* Dexin Yang

## Data source

* [Stock Historical Price Data](https://developer.yahoo.com/api/)
* [WallStreetBets Subreddit Data](https://praw.readthedocs.io/en/stable/)
* [Stock Market News Data](https://www.alphavantage.co/documentation/#intelligence)
* [Inflation Data](https://www.bls.gov/developers/api_signature_v2.htm)
* [GDP Data](https://www.bea.gov/)
* [Covid Data](https://api-ninjas.com/)

## Reference
* [Y. Chen, "Financial News Sentiment Analysis Method Based on WMSA-Bi-LSTM," 2023 4th International Conference on Intelligent Design（ICID）, Xi'an, China, 2023, pp. 319-322, doi: 10.1109/ICID60307.2023.10396691.](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10396691&isnumber=10396668)
* [D. Shah, H. Isah and F. Zulkernine, "Predicting the Effects of News Sentiments on the Stock Market," 2018 IEEE International Conference on Big Data (Big Data), Seattle, WA, USA, 2018, pp. 4705-4708, doi: 10.1109/BigData.2018.8621884.](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8621884&isnumber=8621858)
* [Satyaveer, P. Patel, H. Chandra, P. Pal and S. K. Singh, "A New Hybrid Model ARFIMA-LSTM Combined with News Sentiment Analysis Model for Stock Market Prediction," 2023 Third International Conference on Advances in Electrical, Computing, Communication and Sustainable Technologies (ICAECT), Bhilai, India, 2023, pp. 1-5, doi: 10.1109/ICAECT57570.2023.10118349.](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10118349&isnumber=10117572)