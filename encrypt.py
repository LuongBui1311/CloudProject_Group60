import boto3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from cryptography.fernet import Fernet
from flask import Flask, render_template, request, redirect, url_for, send_file, session, make_response
import boto3
from botocore.exceptions import NoCredentialsError
import os

def encrypt_large_file_with_kms(file_contents, kms_key_id,file_path):
    try:
        region_name='us-east-1'
        kms_client = boto3.client('kms', region_name)
        # Tính toán số lượng phần cần chia
        chunk_size = 16 * 1024   # 4 KB
        file_size = os.path.getsize(file_path)
        num_parts = file_size // chunk_size + (file_size % chunk_size != 0)
        # Chia tệp thành các phần nhỏ và mã hóa từng phần1 
        encrypted_parts = []
        for part_number in range(1, num_parts + 1):
            start_index = (part_number - 1) * chunk_size
            end_index = part_number * chunk_size
            part_data = file_contents[start_index:end_index]
            encrypted_data = encrypt_file_with_kms(part_data, kms_key_id)
            encrypted_parts.append(encrypted_data)
        # Gộp các phần đã mã hóa thành một mảng byte đơn
        encrypted_data = b''.join(encrypted_parts)
        return encrypted_data

    except Exception as e:
        return None

def encrypt_file_with_kms(data, kms_key_id):
    try:
        region_name='us-east-1'
        kms_client = boto3.client('kms', region_name)
        response = kms_client.encrypt(KeyId=kms_key_id, Plaintext=data)
        return response['CiphertextBlob']
    except Exception as e:
        return None
    
# Hàm giải mã (decryption) sử dụng AWS KMS
def decrypt_file_with_kms(encrypted_data, kms_key_id):
    kms_client = boto3.client('kms')

    response = kms_client.decrypt(
        KeyId=kms_key_id,
        CiphertextBlob=encrypted_data
    )

    return response['Plaintext']
