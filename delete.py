from botocore.exceptions import NoCredentialsError

# Hàm xóa file từ S3
def delete_file_from_s3(file_name, bucket_name, s3_client):
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        return True
    except NoCredentialsError:
        return False
    except Exception as e:
        return False
