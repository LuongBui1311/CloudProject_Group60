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
def upload_file_to_s3(file_path, bucket_name, s3_client, kms_key_id):
    try:
        start_time = time.time()
        with open(file_path, 'rb') as file:
            file_contents = file.read()
        # Khóa đối tượng object_key
        object_key = os.path.basename(file_path)
        # Tải lên S3 bằng phương thức put_object
        s3_client.put_object(Body=file_contents, Bucket=bucket_name, Key=object_key)

        end_time = time.time()
        upload_time = end_time - start_time
        print(f"Thời gian tải lên: {upload_time} giây")
        return render_template('file_list.html', upload_time=upload_time)
    except NoCredentialsError:
        return False
    except Exception as e:
        return False
