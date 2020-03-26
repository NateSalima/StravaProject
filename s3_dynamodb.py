import boto3
import os
import psycopg2
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from sqlalchemy import create_engine
import configparser
import decimal
from dynamodb_json import json_util as dyjson
import json

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

json_file = open(os.path.join(ROOT_DIR, 'strava_config.json'), 'r')
json_str = json_file.read()
s3_info = json.loads(json_str)['s3_credentials']
redshift_info = json.loads(json_str)['redshift_credentials']

# AWS s3 Credentials
bucket_name = s3_info['bucket_name']
access_key = s3_info['access_key']
secret_access_key = s3_info['secret_access_key']

# gets json from s3 buckets
def get_json_s3(file_name = "strava_streams.json"):
    client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key
    )
    def get_file(client):
        result = client.get_object(Bucket=bucket_name, Key="StravaData/" + file_name) 
        text = result["Body"].read().decode()
        data = json.loads(text)
        return data
    data = get_file(client) 
    data
    return(data)

# uploads json to dynamodb
def move_json():
    client = boto3.client(
        'dynamodb',
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_access_key,
        region_name='us-west-2'
    )

    streams_json = get_json_s3()
    print("uploading to dynamodb")

    count = 0
    for item in streams_json:
        item = dyjson.dumps(item)
        item = json.loads(item)
        
        client.put_item(
            TableName = 'strava_streams2',
            Item=item
        )
        count += 1
    print(f"added {count} objects to dynamodb")
    print("successfully uploaded to dynamodb")


    


move_json()

