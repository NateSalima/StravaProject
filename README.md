# Strava Data Analysis
This project moves Strava data to a Jupyter notebook and a Dash app on a daily basis using airflow.

# Motivation
I have been wanting to do an end to end data project to get a feel for the different aspects of data science. I was recommended to take a look at the Strava API. Strava is a fitness social media platform that tracks activites such as runs or bike rides. After looking into the data accessable through Strava API my interest was sparked and I started this project.

# Summary Of The Pipeline
![Pipeline Architecture](./images/Architecture.png)
1. First airflow calls a python script to grab only new data from Strava and upload it as two seperate JSON files to an S3 bucket one file containing streaming data and one file containting activity data.

2. After the JSON files are uploaded to S3 Airflow will then run 2 seperate scripts simultaniously to transform the data and load and seperatly load the streaming data into DynamoDB and the Activity Data into Redshift.

3. From there the Jupyter notebooks and Dash app will directly query the Databases.

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

## Setup S3
1. Click Create Bucket
    ![S3 Setup](./images/S3Setup1.png)
2. Fill in the following fields
    ![S3 Setup](./images/S3Setup2.png)
3. For my project I didn't block public access just to make it easier to access and since I am fine with this data being shared.
![S3 Setup](./images/S3Setup3.png)
4. Click 'Create Bucket'

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

5.  Verify Airflow is running ![Airflow Setup](./images/AirflowSetup2.png)

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
4. Jupyter will start running at http://localhost:8888/ ![Jupyter Setup](./images/JupyterSetup1.png)

5. Verify Jupyter is running in the browser.[Jupyter Setup](./images/JupyterSetup2.png)


## Setup Dash
TODO
# Python Code in Airflow
TODO
# Dash App
TODO
# Jupyter Notebook
TODO