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

        # Mở tập tin đường dẫn file_path để đọc nội dung
        # rb: Đọc dạng nhị phân (đọc hình ảnh, video, docx)
        # file_content: Biến chứa nội dung sau khi đọc
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
    # ngoại lệ
    except NoCredentialsError:
        return False
    except Exception as e:
        return False
    # try:
    #     with open(file_path, 'rb') as file:
    #         file_contents = file.read()
    #         # Determine the MIME type of the file
    #         # mime_type, _ = mimetypes.guess_type(file_path)
    #     object_key = os.path.basename(file_path)
    #     #encrypted_data = encrypt.encrypt_file_with_kms(file_contents, kms_key_id, file_path)
    #     #encrypted_data = encrypt.encrypt_large_file_with_kms(file_contents, kms_key_id, file_path)
    #     if encrypted_data is not None:
    #         s3_client.put_object(Body=encrypted_data, Bucket=bucket_name, Key=object_key)
    #         return True
    #     else:
    #         return False
    # except NoCredentialsError:
    #     return False
    # except Exception as e:
    #     return False
