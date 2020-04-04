import json
import boto3
import os
import psycopg2
import numpy as np
import pandas as pd
from pandas import json_normalize
from sqlalchemy import create_engine
from datetime import timezone
import configparser


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

json_file = open(os.path.join(ROOT_DIR, 'strava_config1.json'), 'r')
json_str = json_file.read()
s3_info = json.loads(json_str)['s3_credentials']
redshift_info = json.loads(json_str)['redshift_credentials']

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

df_names = ['name',
            'id',  
            'type',
            'start_date',
            'elapsed_time_min',
            'distance_km',
            'average_speed_ms',
            'workout_duration',
            'total_elevation_gain_m',
            'manual_entry']


# gets most recent start_date that is already uploaded in redshift
# returnes date/time value
def last_activity_date():
    engine = create_engine(f'redshift+psycopg2://{iam_user}:{iam_password}@{endpoint}/{db_name}')
    df = pd.read_sql_query(f'SELECT start_date FROM public.{table_name} ORDER BY start_date DESC LIMIT 1',con=engine)
    return(df.loc[0]['start_date']) 

def get_json_s3(file_name = "strava.json"):
    client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key
    )
    result = client.get_object(Bucket=bucket_name, Key=f"StravaData/{file_name}") 
    text = result["Body"].read().decode()
    data = json.loads(text)
    df = pd.DataFrame()
    for i in data:
        temp_df = pd.DataFrame.from_dict(json_normalize(i))
        df = pd.concat([df, temp_df])
    return(df)

def upload_redshift():
    df = get_json_s3()
    df.columns = df_names
    last_date = last_activity_date()
    print(last_date.replace(tzinfo=timezone.utc).isoformat())
    last_date = last_date.replace(tzinfo=timezone.utc).isoformat()
    df['start_date'] = pd.to_datetime(df['start_date'])

    # get only new records
    df = df[df['start_date'] > last_date]
    if df.empty:
        print('no data to add')
    else:
        print(f"Added {df.shape[0]} activity records")
        del df['workout_duration']
        df.set_index('id', inplace=True)
        engine = create_engine(f'redshift+psycopg2://{iam_user}:{iam_password}@{endpoint}/{db_name}')
        df.to_sql('strava', con=engine, if_exists='append')

def first_time():
    df = get_json_s3()
    df.columns = df_names
    del df['workout_duration']
    df.set_index('id', inplace=True)
    print(df.head())
    engine = create_engine(f'redshift+psycopg2://{iam_user}:{iam_password}@{endpoint}/{db_name}')
    df.to_sql('strava', con=engine, if_exists='append')

if __name__ == '__main__':
    upload_redshift()