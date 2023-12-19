import boto3
from botocore.exceptions import NoCredentialsError
from botocore.client import Config

# Hàm tạo đường link chia sẻ
def generate_shared_link(aws_access_key_id, bucket_name, aws_secret_access_key,filename):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=Config(signature_version='s3v4')  
        )


        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket_name, 'Key': filename},
            ExpiresIn=3600,
        )
        return url
    except NoCredentialsError:
        print("Thông tin đăng nhập không khả dụng")
        return None
