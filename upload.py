from botocore.exceptions import NoCredentialsError
import encrypt

# Hàm upload file lên S3 với mã hóa SSE-KMS
def upload_encrypted_file_to_s3_with_kms(file_path, bucket_name, s3_client, kms_key_id):
    try:
        print(bucket_name, kms_key_id)
        with open(file_path, 'rb') as file:
            file_contents = file.read()
            
            # Determine the MIME type of the file
            #mime_type, _ = mimetypes.guess_type(file_path)
        print(kms_key_id)
        encrypted_data = encrypt.encrypt_file_with_kms(file_contents, kms_key_id)

        if encrypted_data is not None:
            s3_client.put_object(Body=encrypted_data, Bucket=bucket_name, Key=file_path)
            return True
        else:
            return False
    except NoCredentialsError:
        return False
    except Exception as e:
        return False
