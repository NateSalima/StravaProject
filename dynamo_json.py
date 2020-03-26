import boto3
import os
import json
from dynamodb_json import json_util as dyjson
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import plotly.express as px 

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

json_file = open(os.path.join(ROOT_DIR, 'strava_config.json'), 'r')
json_str = json_file.read()

s3_info = json.loads(json_str)['s3_credentials']

# AWS s3 Credentials
bucket_name = s3_info['bucket_name']
access_key = s3_info['access_key']
secret_access_key = s3_info['secret_access_key']

with open('mapbox_tkn.txt', 'r') as f: 
    mapbox_key = f.read().strip()


client = boto3.client(
        'dynamodb',
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_access_key,
        region_name='us-west-2'
    )

response = client.get_item(
    TableName='strava_streams',
    Key={'id': {'N': '3068703155'}}
)

data=dyjson.loads(response)
print(type(data))

df = pd.DataFrame(data.get('Item'))
print(df)

df[['lat', 'lng']]= pd.DataFrame(df['latlng'].values.tolist(), index = df.index)
df = df.drop(['latlng'], axis=1)
print(df)

fig = px.line_mapbox(df, lat="lat", lon="lng" )
fig.update_layout(mapbox_style="Dark") 
fig.show()