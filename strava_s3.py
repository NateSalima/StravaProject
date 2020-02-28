from stravalib import Client
import pandas as pd
from flask import request

import os
import json
import data


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

json_file = open(os.path.join(ROOT_DIR, 'strava_config.json'), 'r')
json_str = json_file.read()
api_info = json.loads(json_str)['strava_api']

client_id = api_info['client_id']
client_secret = api_info['client_secret']
refresh_token = api_info['refresh_token']
bucket_name = ['datascienceproject-bucket']
code = ['code']



def get_activity_data(date_start = pd.to_datetime('today', format = "%Y-%m-%d") - pd.DateOffset(days=30),
                      date_end = pd.to_datetime('today', format = "%Y-%m-%d")):
    client = Client()
    access_token = _get_access_token(client, client_id, client_secret, refresh_token)
    client = Client(access_token=access_token)
    print(client.get_athlete())

    activity_df, activity_streams = _get_activity_data(client,
                                                       date_start = date_start,
                                                       date_end = date_end)
    return activity_df, activity_streams


def _get_activity_data(client,
                       date_start=pd.to_datetime('today', format="%Y-%m-%d") - pd.DateOffset(days=30),
                       date_end=pd.to_datetime('today', format="%Y-%m-%d"),
                       resolution = 'high',
                       types = ['time', 'distance', 'altitude', 'latlng']):

    activity_df = pd.DataFrame()
    activity_streams = dict()
    
    for activity in client.get_activities(after=date_start,
                                          before=date_end):
        streams = client.get_activity_streams(activity.id,
                                              types=types,
                                              series_type='time',
                                              resolution=resolution)
        if not activity.manual:
            print(activity.id)
            for key, value in streams.items():
                streams[key] = value.data
                print(value.data)
            activity_streams[activity.id] = pd.DataFrame(streams)
        
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
    return activity_df, activity_streams



def _get_access_token(client, client_id, client_secret, refresh_token):
    client = Client()
    token_response = client.refresh_access_token(client_id=client_id,
                                      client_secret=client_secret,
                                      refresh_token=refresh_token)

    access_token = token_response['access_token']

    return access_token


test = get_activity_data()
#print(test[1])
print(type(test[0])) 