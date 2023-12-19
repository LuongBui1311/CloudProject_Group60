import boto3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.fernet import Fernet

# Hàm mã hóa (encryption) sử dụng AWS KMS
def encrypt_file_with_kms(data, kms_key_id):
    kms_client = boto3.client('kms')

    response = kms_client.encrypt(
        KeyId=kms_key_id,
        Plaintext=data
    )

    return response['CiphertextBlob']


# Hàm giải mã (decryption) sử dụng AWS KMS
def decrypt_file_with_kms(encrypted_data, kms_key_id):
    kms_client = boto3.client('kms')

    response = kms_client.decrypt(
        KeyId=kms_key_id,
        CiphertextBlob=encrypted_data
    )

    return response['Plaintext']
