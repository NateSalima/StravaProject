import boto3
import os
import psycopg2
import json
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from sqlalchemy import create_engine
import configparser
import decimal
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

json_file = open(os.path.join(ROOT_DIR, 'strava_config.json'), 'r')
json_str = json_file.read()
s3_info = json.loads(json_str)['s3_credentials']
redshift_info = json.loads(json_str)['redshift_credentials']

# AWS s3 Credentials
bucket_name = s3_info['bucket_name']
access_key = s3_info['access_key']
secret_access_key = s3_info['secret_access_key']

def get_json_s3(file_name = "strava_streams.json"):
    client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key
    )
    result = client.get_object(Bucket=bucket_name, Key="StravaData/" + file_name) 
    text = result["Body"].read().decode()
    data = json.loads(text)
    return(data)

def move_json():
    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_access_key,
        region_name='us-west-2'
    )

    table = dynamodb.Table('strava_streams')

    streams_json = get_json_s3()
    print("uploading to dynamodb")

    for item in streams_json:
        id = item["id"]
        altitude = list(map(round_float_to_decimal, item["altitude"]))
        latlng = [list(map(round_float_to_decimal , i)) for i in item["latlng"]]
        distance = list(map(round_float_to_decimal, item["distance"]))
        time_elapsed = item["time"] 

        table.put_item(
            Item={
                'id': id,
                'altitude': altitude,
                'latlng': latlng,
                'distance': distance,
                'time': time_elapsed
            }
        )
    print("successfully uploaded to dynamodb")

# workaround to decimal error
def round_float_to_decimal(float_value):
    with decimal.localcontext(boto3.dynamodb.types.DYNAMODB_CONTEXT) as decimalcontext:
        decimalcontext.traps[decimal.Inexact] = 0
        decimalcontext.traps[decimal.Rounded] = 0
        decimal_value = decimalcontext.create_decimal_from_float(float_value)
    return decimal_value



move_json()

