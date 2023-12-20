from botocore.exceptions import NoCredentialsError
import time
# Hàm xóa file từ S3
def delete_file_from_s3(file_name, bucket_name, s3_client):
    try:
        start_time = time.time()
        s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        end_time = time.time()
        delete_time = end_time - start_time
        return True
    except NoCredentialsError:
        return False
    except Exception as e:
        return False
