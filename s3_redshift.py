import json
import boto3
import os
import psycopg2
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from sqlalchemy import create_engine
import configparser


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

json_file = open(os.path.join(ROOT_DIR, 'strava_config.json'), 'r')
json_str = json_file.read()
s3_info = json.loads(json_str)['s3_credentials']
redshift_info = json.loads(json_str)['redshift_credentials']

# AWS s3 Credentials
bucket_name = s3_info['bucket_name']
access_key = s3_info['access_key']
secret_access_key = s3_info['secret_access_key']

# AWS redshift credentials
db_name = redshift_info['db_name']
iam_user = redshift_info['iam_user']
iam_password = redshift_info['iam_password']


# gets most recent start_date that is already uploaded in redshift
# returnes date/time value
def last_activity_date():
    engine = create_engine(f'redshift+psycopg2://{iam_user}:{iam_password}@redshift-cluster-1.c3ubemyorhfw.us-west-2.redshift.amazonaws.com:5439/{db_name}')
    df = pd.read_sql_query('SELECT start_date FROM public.test ORDER BY start_date DESC LIMIT 1',con=engine)
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
    df = pd.DataFrame()
    df = get_json_s3()
    last_date = last_activity_date()
    df['start_date'] = pd.to_datetime(df['start_date'])
    
    # get only new records
    df = df[(df['start_date'] > last_date)]
    if df.empty:
        print('no data to add')
    else:
        print(f"Added {df.shape[0]} activity records")
        df.set_index('activity_id', inplace=True)
        engine = create_engine(f'redshift+psycopg2://{iam_user}:{iam_password}@redshift-cluster-1.c3ubemyorhfw.us-west-2.redshift.amazonaws.com:5439/{db_name}')
        df.to_sql('test', con=engine, if_exists='append')

def first_time():
    df = get_json_s3()
    df.set_index('activity_id', inplace=True)
    engine = create_engine(f'redshift+psycopg2://{iam_user}:{iam_password}@redshift-cluster-1.c3ubemyorhfw.us-west-2.redshift.amazonaws.com:5439/{db_name}')
    df.to_sql('test', con=engine, if_exists='append')

#first_time()

upload_redshift()