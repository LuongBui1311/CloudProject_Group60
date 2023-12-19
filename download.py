from botocore.exceptions import NoCredentialsError
import encrypt

# Hàm tải file từ S3 với giải mã
def download_decrypted_file_from_s3_with_kms(file_name, bucket_name, s3_client, kms_key_id):
    try:
        # Download the encrypted file content from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        encrypted_data = response['Body'].read()

        # Decrypt the file content
        decrypted_data = encrypt.decrypt_file_with_kms(encrypted_data, kms_key_id)

        return decrypted_data
    except NoCredentialsError:
        return None
    except Exception as e:
        return None
