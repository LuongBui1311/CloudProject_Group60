import boto3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from cryptography.fernet import Fernet
from flask import Flask, render_template, request, redirect, url_for, send_file, session, make_response
import boto3
from botocore.exceptions import NoCredentialsError

# Hàm mã hóa (encryption) sử dụng AWS KMS
# def encrypt_file_with_kms(data, kms_key_id):
#     kms_client = boto3.client('kms')

#     response = kms_client.encrypt(
#         KeyId=kms_key_id,
#         Plaintext=data
#     )

#     return response['CiphertextBlob']
def encrypt_file_with_kms(data, kms_key_id):
   
        access_key = session.get('access_key')
        region_name='us-east-1'
        # Khởi tạo client KMS với region_name đã chỉ định
        kms_client = boto3.client('kms', region_name)
        # Mã hóa dữ liệu bằng KMS
        try:
            response = kms_client.encrypt(KeyId=kms_key_id, Plaintext=data)
    # Thực hiện xử lý kết quả ở đây
        except kms_client.exceptions.NotFoundException as e:
            print(f"KMS key not found: {e}")
        except kms_client.exceptions.DisabledException as e:
            print(f"KMS key is disabled: {e}")
        except kms_client.exceptions.InvalidKeyUsageException as e:
            print(f"Invalid key usage: {e}")
        except kms_client.exceptions.KMSInvalidStateException as e:
            print(f"Invalid KMS state: {e}")
        except Exception as e:
            print(f"Error encrypting data with KMS: {e}")
        print("Lương")
        # Trả về dữ liệu đã mã hóa
        return response['CiphertextBlob']
    

# Hàm giải mã (decryption) sử dụng AWS KMS
def decrypt_file_with_kms(encrypted_data, kms_key_id):
    kms_client = boto3.client('kms')

    response = kms_client.decrypt(
        KeyId=kms_key_id,
        CiphertextBlob=encrypted_data
    )

    return response['Plaintext']
