from botocore.exceptions import NoCredentialsError

# Hàm tải tất cả các files từ S3
def read_all_files_from_s3(bucket_name, s3_client):
    try:
        objects = s3_client.list_objects(Bucket=bucket_name)['Contents']
        return [obj['Key'] for obj in objects]
    except NoCredentialsError:
        return []
    except Exception as e:
        return []
    