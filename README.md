# Strava Data Analysis
This project moves Strava data to a Jupyter notebook and a Dash app on a daily basis using airflow.

# Summary of Pipeline
![Pipeline Architecture](./images/Architecture.png)
# Prerequsites
This project assumes the user already has an AWS and Strava account and that the user also has [docker setup](https://www.strava.com/settings/api) on their machine.

# Getting Started
1. Clone Repository
## Setup Strava API
In order to use the strava API you have to create and register an app
1. Go to the Strava [API Setup Page.](https://www.strava.com/settings/api)
2.  Fill out the API app form
![Strava API Setup](./images/stravaappsetup1.png)
3. Once this is done you should be able to see all of the necessary credentials that we will need for the app.
![Strava API Setup](./images/stravaappsetup2.png)

## Setup DynamoDB
1. Open up the AWS console
2. Navigate to the DynamoDB dashboard
3. Click 'Create Table'
![DynamoDB Setup](./images/DynamoDBSetup1.png)
4. Fill in the following fields
![DynamoDB Setup](./images/DynamoDBSetup2.png)
5. Click Create

## Setup Redshift
1. Open up the AWS console
2. Navigate to the Redshift dashboard
3. Click 'Create Cluster' in the upper right hand corner
![Redshift Setup](./images/RedshiftSetup1.png)
4. Fill in the following fields
![Redshift Setup](./images/RedshiftSetup2.png)
![Redshift Setup](./images/RedshiftSetup3.png)
5. Click Create Cluster
![Redshift Setup](./images/RedshiftSetup4.png)
6. Next navigate to the editor tab
7. Enter in this sql statement to create the table and click run
    ```
    CREATE TABLE strava (
    id						int8,
    name					varchar(350),
    start_date				TIMESTAMP,
    average_speed_ms		real,
    distance_km				real,
    elapsed_time_min		int,
    total_elevation_gain_m 	real,
    type					varchar(14),
    manual_entry			bool
    )
    ```
    ![Redshift Setup](./images/RedshiftSetup5.png)
##

## Setup Airflow Using A Dockerfile
1. Navigate to the [Data_Retrieval](./Data_Retrieval) folder inside the repo
2. Run the following command to build an image from the Dockerfile
    ```
    docker build -f Data.Dockerfile -t strava_data:1.0 .
    ```
3. To run the image execute the following command
    ```
    docker run -p 8080:8080 --name sd -v $(pwd)/dags:/usr/local/airflow/dags strava_data:1.0
    ```
4. Airflow will start running at http://localhost:8080/ ![Airflow Setup](./images/AirflowSetup1.png)

## Setup Jupyter Using A Dockerfile
1. Navigate to the [Jupyter](./Jupyter) folder inside the repo
2. Run the following command to build an image from the Dockerfile
    ```
    docker build -f Jupyter.Dockerfile -t strava_jupyter:1.0 .
    ```
3. To run the image execute the following command
    ```
    docker run -p 8888:8888 --name sj -v $(pwd):/home/jovyan/  strava_jupyter:1.0 
    ```
4. Airflow will start running at http://localhost:8888/ ![Jupyter Setup](./images/JupyterSetup1.png)
## Setup Dash
Currently Dash is not setup and is a work in progress
