import boto3
from botocore.client import Config

def create_s3_client(access_key, secret_key):
    s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')  
        )
    return s3_client

def create_s3_resource(access_key, secret_key):
    s3_resource = boto3.resource(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')  
        )
    return s3_resource
