from stravalib import Client
import pandas as pd
from flask import request

import boto3
import os
import json
import data


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

json_file = open(os.path.join(ROOT_DIR, 'strava_config.json'), 'r')
json_str = json_file.read()
api_info = json.loads(json_str)['strava_api']
s3_info = json.loads(json_str)['s3_credentials']

# Strava Credentials
client_id = api_info['client_id']
client_secret = api_info['client_secret']
refresh_token = api_info['refresh_token']

# AWS s3 Credentials
bucket_name = s3_info['bucket_name']
access_key = s3_info['access_key']
secret_access_key = s3_info['secret_access_key']


# gets activity data from desired dates, default is set to 30 days
# inputs:   date_start: desired start date, date_end: desired end date
# outputs:  activity_df: dataframe of activity data, activity_stream: dataframe of activities stream,
#           stream_list: list of actrivity objects containing various streams from each activity
def get_activity_data(date_start = pd.to_datetime('today', format = "%Y-%m-%d") - pd.DateOffset(days=30),
                      date_end = pd.to_datetime('today', format = "%Y-%m-%d")):
    client = Client()
    access_token = _get_access_token(client, client_id, client_secret, refresh_token)
    client = Client(access_token=access_token)
    activity_df = pd.DataFrame()
    stream_list = []

    activity_list, activity_df, activity_streams, stream_list = _get_activity_data(client,
                                                        date_start = date_start,
                                                        date_end = date_end)
    return activity_list, activity_df, activity_streams, stream_list


def _get_activity_data(client,
                       date_start = pd.to_datetime('today', format="%Y-%m-%d") - pd.DateOffset(days=30),
                       date_end = pd.to_datetime('today', format="%Y-%m-%d"),
                       resolution = 'high',
                       types = ['altitude', 'latlng', 'distance', 'time']):

    activity_df = pd.DataFrame()
    activity_streams = dict()

    stream_list = []
    activity_list = []
    for activity in client.get_activities(after=date_start,
                                          before=date_end):
        streams = client.get_activity_streams(activity.id,
                                              types=types,
                                              series_type='time',
                                              resolution=resolution)
        if not activity.manual:
            activity_dict = {'id': activity.id}
            for key, value in streams.items():
                streams[key] = value.data
                activity_dict.update({key: value.data})
            activity_streams[activity.id] = pd.DataFrame(streams)
            stream_list.append(activity_dict)

        temp_dict = {'activity_name': activity.name,
                    'activity_id': activity.id,
                    'started_at': str(activity.start_date),
                    'moving_time_min': int(activity.moving_time.seconds / 60),
                    'distance_km': round(activity.distance.num / 1000, 1),
                    'avg_speed_ms': str(activity.average_speed),
                    'total_workout_duration': str(activity.elapsed_time),
                    'total_elevation_gain_m': str(activity.total_elevation_gain),
                    'manual_entry': activity.manual,
                    'description': activity.description
                    }
        activity_list.append(temp_dict)
        activity_df = activity_df.append(pd.DataFrame([{'activity_name': activity.name,
                                                        'activity_id': activity.id,
                                                        'started_at': activity.start_date,
                                                        'moving_time_min': int(activity.moving_time.seconds / 60),
                                                        'distance_km': round(activity.distance.num / 1000, 1),
                                                        'avg_speed_ms': activity.average_speed,
                                                        'total_workout_duration': activity.elapsed_time,
                                                        'total_elevation_gain_m': activity.total_elevation_gain,
                                                        'manual_entry': activity.manual,
                                                        'description': activity.description
                                                        }]))
    return activity_list, activity_df, activity_streams, stream_list


# gets new access token if you already hava a refresh token for an athlete
def _get_access_token(client, client_id, client_secret, refresh_token):
    token_response = client.refresh_access_token(client_id=client_id,
                                      client_secret=client_secret,
                                      refresh_token=refresh_token)

    access_token = token_response['access_token']

    return access_token


def upload_s3(json_obj, upload_name = "strava.json"):

    with open(upload_name, 'w') as fp:
        json.dump(json_obj, fp)

    # S3 Connect
    client = boto3.client(
        's3',
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_access_key
    )
    client.upload_file(upload_name, bucket_name, "StravaData/" + upload_name)
    os.remove(upload_name)


upload_data = get_activity_data()
upload_s3(upload_data[0], upload_name = "strava.json")
upload_s3(upload_data[3], upload_name = "strava_streams.json")