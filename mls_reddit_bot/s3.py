import boto3
import json
import os
import requests

from botocore.exceptions import ClientError

from mls_reddit_bot import log

s3 = None

def write_json(bucket, key, data):
    log.info(f'caching data to s3://{bucket}/{key}')
    s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(data, indent=4))

# if we haven't already cached, fetch json from a url
def read_or_fetch_json(url, bucket, key, force=False):
    global s3
    if not s3:
        s3 = boto3.client('s3')

    data = {}
    try:
        result = s3.get_object(Bucket=bucket, Key=key)
        text = result["Body"].read().decode()
        data = json.loads(text)
    except ClientError as ex:
        pass

    # skip fetch if we already have, unless --force is requested
    if data and not force:
        log.info(f'fetched match data from s3://{bucket}/{key}, skipping fetch from the API')
    else:
        # make the api call
        log.info(f'fetching json data from {url}')
        response = requests.get(url)
        data = response.json()

        # write
        write_json(bucket, key, data)

    return data
