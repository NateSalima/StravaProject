from stravalib import Client
import pandas as pd
from flask import request
from sqlalchemy import create_engine

import boto3
import os
import json
#import data
import time
import re


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

json_file = open(os.path.join(ROOT_DIR, 'strava_config1.json'), 'r')
json_str = json_file.read()
api_info = json.loads(json_str)['strava_api']
s3_info = json.loads(json_str)['s3_credentials']
redshift_info = json.loads(json_str)['redshift_credentials']

# Strava Credentials
client_id = api_info['client_id']
client_secret = api_info['client_secret']
refresh_token = api_info['refresh_token']

# AWS s3 Credentials
bucket_name = s3_info['bucket_name']
access_key = s3_info['access_key']
secret_access_key = s3_info['secret_access_key']

# AWS redshift credentials
db_name = redshift_info['db_name']
table_name = redshift_info['table_name']
endpoint = redshift_info['endpoint']
iam_user = redshift_info['iam_user']
iam_password = redshift_info['iam_password']


# gets most recent start_date that is already uploaded in redshift
# returns date/time value
def last_activity_date():
    engine = create_engine(f'redshift+psycopg2://{iam_user}:{iam_password}@{endpoint}/{db_name}')
    df = pd.read_sql_query(f'SELECT start_date FROM public.{table_name} ORDER BY start_date DESC LIMIT 1',con=engine)
    return(df.loc[0]['start_date']) 
 
#removes all non-numeric items from an object and converts to float
def remove_non_numeric(data):
    data = str(data)
    non_decimal = re.compile(r'[^\d.]+')
    non_decimal.sub('', data)
    return(float(non_decimal.sub('', data)))

# gets activity data from desired dates, default is set to 30 days
# inputs:   date_start: desired start date, date_end: desired end date
# outputs:  activity_df: dataframe of activity data, activity_stream: dataframe of activities stream,
#           stream_list: list of actrivity objects containing various streams from each activity
def get_activity_data(date_start = last_activity_date(),
                      date_end = pd.to_datetime('today', format = "%Y-%m-%d %H:%M:%S")):
    client = Client()
    access_token = _get_access_token(client, client_id, client_secret, refresh_token)
    client = Client(access_token=access_token)
    stream_list = []

    activity_list, stream_list = _get_activity_data(client,
                                                        date_start = date_start,
                                                        date_end = date_end)
    return activity_list, stream_list


def _get_activity_data(client,
                       date_start = last_activity_date(),
                       date_end = pd.to_datetime('today', format="%Y-%m-%d %H:%M:%S"),
                       resolution = 'high',
                       types = ['altitude', 'latlng', 'distance', 'time']):

    stream_list = []
    activity_list = []
    for activity in client.get_activities(after=date_start,
                                          before=date_end):
        streams = client.get_activity_streams(activity.id,
                                              types=types,
                                              series_type='time',
                                              resolution=resolution)
        if not activity.manual:
            activity_dict = {'partition': '1',
                             'id': activity.id,
                             'name': activity.name}
            activity_dict.update({'date': str(activity.start_date)})
            for key, value in streams.items():
                streams[key] = value.data
                activity_dict.update({key: value.data})
            stream_list.append(activity_dict)

        temp_dict = {'activity_name': activity.name,
                    'activity_id': activity.id,
                    'type': activity.type,
                    'start_date': str(activity.start_date),
                    'moving_time_min': int(activity.moving_time.seconds / 60),
                    'distance_km': round(activity.distance.num / 1000, 1),
                    'avg_speed_ms': remove_non_numeric(activity.average_speed),
                    'total_workout_duration': str(activity.elapsed_time),
                    'total_elevation_gain_m': remove_non_numeric(activity.total_elevation_gain),
                    'manual_entry': activity.manual,
                    }
        activity_list.append(temp_dict)
    return activity_list, stream_list


# gets new access token if you already hava a refresh token for an athlete
def _get_access_token(client, client_id, client_secret, refresh_token):
    token_response = client.refresh_access_token(client_id=client_id,
                                      client_secret=client_secret,
                                      refresh_token=refresh_token)

    access_token = token_response['access_token']

    return access_token


# uploads file to s3 client
def upload_s3(upload_data, upload_name = "strava.json"):
    # S3 Connect
    client = boto3.client(
        's3',
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_access_key
    )
    # gets only new data 
    updated_data = _upload_s3(client, upload_data, file_name = upload_name)
    with open(upload_name, 'w') as fp:
        json.dump(updated_data, fp)
    client.upload_file(upload_name, bucket_name, "StravaData/" + upload_name)
    os.remove(upload_name)

# adds only new data to the json obhect and returns the object
def _upload_s3(client, upload_data, file_name = "stava.json"):
    new_data = upload_data
    past_data = get_past_data(client, file_name)
    updated_data = past_data
    def check_past(i):
        for j in past_data:
            if i == j:
                print("data already in file")
                return
        return i

    new_object_counter = 0
    for i in new_data:
        temp = check_past(i)
        if temp is not None:
            updated_data.append(temp)
            new_object_counter += 1
    print(str(new_object_counter) + " objects added")
    return(updated_data)


# gets past data from s3
def get_past_data(client, file_name):
    result = client.get_object(Bucket= bucket_name, Key="StravaData/" + file_name) 
    text = result["Body"].read().decode()
    data = json.loads(text)
    print("Data Sucessfully Retrieved From S3")
    return(data)


print(last_activity_date())
#print(df.loc[0])

upload_data = get_activity_data()
upload_s3(upload_data[0], upload_name = "strava.json")
upload_s3(upload_data[1], upload_name = "strava_streams.json")