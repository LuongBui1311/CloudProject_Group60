from botocore.exceptions import NoCredentialsError
import encrypt
import os
import time
from flask import Flask, render_template, request, redirect, url_for, send_file, session, make_response
import boto3
from botocore.client import Config
import delete
import share
import upload
import time
import load
import create_client
# Hàm upload file lên S3 với mã hóa SSE-KMS
def upload_file_to_s3(file, aws_access_key_id, aws_secret_access_key, BUCKETNAME):
    bucket_name = BUCKETNAME
    
    try:
        # Tạo đối tượng S3 từ phiên làm việc
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        # Định dạng tên tệp để chứa trong thư mục
        acl = "private"
        file_key = file.filename

        print('Start upload...')
        print('File : ' + file.filename)
        start_time = time.time()
        s3.upload_fileobj(file, bucket_name, file_key, ExtraArgs={"ACL": acl, "ContentType": file.content_type}) 
        end_time = time.time()
        upload_time = round(end_time - start_time, 3)

        message = "File was uploaded to /" + file.filename + "\nTime: " + str(upload_time) + "s"

        return message
    except Exception as e:
        return ""