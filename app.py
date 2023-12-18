from flask import Flask, render_template, request, redirect, url_for, send_file, session, make_response
import boto3
from botocore.exceptions import NoCredentialsError
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.fernet import Fernet
#import mimetypes

app = Flask(__name__, static_folder='static')
app.secret_key = 'DQ0oU97ZLZyo4Jzd2duUsvgZ76P3SzLYHeWueykN'  # Replace 'your_secret_key' with a secure and unique key

# Constants
NUM_BYTES_FOR_LEN = 4
BUCKETNAME = "endsemproject"


# Hàm tạo client S3
def create_s3_client(access_key, secret_key):
    return boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)


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


# Hàm tải file từ S3 với giải mã
def download_decrypted_file_from_s3_with_kms(file_name, bucket_name, s3_client, kms_key_id):
    try:
        # Download the encrypted file content from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        encrypted_data = response['Body'].read()

        # Decrypt the file content
        decrypted_data = decrypt_file_with_kms(encrypted_data, kms_key_id)

        return decrypted_data
    except NoCredentialsError:
        return None
    except Exception as e:
        return None


# Hàm tải tất cả các files từ S3
def read_all_files_from_s3(bucket_name, s3_client):
    try:
        objects = s3_client.list_objects(Bucket=bucket_name)['Contents']
        return [obj['Key'] for obj in objects]
    except NoCredentialsError:
        return []
    except Exception as e:
        return []


# Hàm upload file lên S3 với mã hóa SSE-KMS
def upload_encrypted_file_to_s3_with_kms(file_path, bucket_name, s3_client, kms_key_id):
    try:
        print(bucket_name, kms_key_id)
        with open(file_path, 'r') as file:
            file_contents = file.read()
            
            # Determine the MIME type of the file
            #mime_type, _ = mimetypes.guess_type(file_path)

        encrypted_data = encrypt_file_with_kms(file_contents, kms_key_id)

        if encrypted_data is not None:
            s3_client.put_object(Body=encrypted_data, Bucket=bucket_name, Key=file_path)
            return True
        else:
            return False
    except NoCredentialsError:
        return False
    except Exception as e:
        return False


# Hàm xóa file từ S3
def delete_file_from_s3(file_name, bucket_name, s3_client):
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        return True
    except NoCredentialsError:
        return False
    except Exception as e:
        return False


# Hàm tạo đường link chia sẻ
def generate_shared_link(file_name, bucket_name, s3_client):
    try:
        # Generate a pre-signed URL with expiration time (e.g., valid for 1 hour)
        expiration_time = 3600  # 1 hour in seconds
        shared_link = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name},
            ExpiresIn=expiration_time
        )

        return shared_link
    except Exception as e:
        return None


# Route cho trang đăng nhập
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        access_key = request.form['access_key']
        secret_key = request.form['secret_key']
        kms_key_id = request.form['kms_key_id']

        # # Store data in the session
        session['access_key'] = access_key
        session['secret_key'] = secret_key
        session['kms_key_id'] = kms_key_id

        return redirect(url_for('file_list'))
        # return f"<h1>{access_key}</h1>"
        # return redirect(url_for('/files/abc'))

    return render_template('login.html')


@app.route('/files/abc', methods=['GET', 'POST'])
def abc():
    if 'access_key' in session:
        access_key = session['access_key']
        return f"<h1>{access_key}</h1>"
    return "abc"


@app.route('/logout')
def logout():
    # Nhận access_key, secret_key, kms_key_id từ form đăng nhập
    access_key = session.get('access_key')
    secret_key = session.get('secret_key')
    kms_key_id = session.get('kms_key_id')

    # For example, you might want to clear the stored access_key, secret_key, and kms_key_id
    # Instead of using session.clear(), you can clear specific session variables
    session.pop('access_key', None)
    session.pop('secret_key', None)
    session.pop('kms_key_id', None)

    # Redirect the user back to the login page
    return redirect(url_for('login'))


# Route cho trang hiển thị danh sách tệp tin
@app.route('/files', methods=['GET', 'POST'])
def file_list():
    # Nhận access_key, secret_key, kms_key_id từ form đăng nhập
    access_key = session.get('access_key')
    secret_key = session.get('secret_key')
    kms_key_id = session.get('kms_key_id')

    # Tạo client S3
    s3_client = create_s3_client(access_key, secret_key)

    # Đọc danh sách tệp tin từ S3
    files = read_all_files_from_s3(BUCKETNAME, s3_client)

    # Hiển thị danh sách tệp tin
    return render_template('file_list.html', files=files,
                           access_key=access_key, secret_key=secret_key, kms_key_id=kms_key_id, s3_client=s3_client)
    # if 'access_key' in session:
    #     access_key = session['access_key']
    #     return f"<h1>{access_key}</h1>"
    # return "abc"


# Route cho thao tác upload tệp tin
@app.route('/files/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # # Retrieve data from the session
        access_key = session.get('access_key')
        secret_key = session.get('secret_key')
        kms_key_id = session.get('kms_key_id')

        # if 'access_key' in session:
        #     access_key = session['access_key']
        #     return f"<h1>{access_key}</h1>"
        # return "abc"

        # # Tạo client S3
        s3_client = create_s3_client(access_key, secret_key)
        #
        # # Upload file
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Lưu file tạm thời và upload lên S3
                file_path = f"{file.filename}"
                file.save(file_path)

                if upload_encrypted_file_to_s3_with_kms(file_path, BUCKETNAME, s3_client, kms_key_id):
                    return redirect(url_for('file_list'))
                else:
                    return "Lỗi khi upload file"
                    

        return "Không có file được chọn"

    return render_template('upload_file.html')
    # if 'access_key' in session:
    #     access_key = session['access_key']
    #     return f"<h1>{access_key}</h1>"
    # return "abc"

# Route cho thao tác xóa tệp tin
@app.route('/delete/<file_name>')
def delete_file(file_name):
    # Nhận access_key, secret_key, kms_key_id từ form đăng nhập
    access_key = request.args.get('access_key')
    secret_key = request.args.get('secret_key')
    kms_key_id = request.args.get('kms_key_id')

    # Tạo client S3
    s3_client = create_s3_client(access_key, secret_key)

    # Xóa file từ S3
    if delete_file_from_s3(file_name, BUCKETNAME, s3_client):
        return redirect(url_for('file_list', access_key=access_key, secret_key=secret_key, kms_key_id=kms_key_id))
    else:
        return "Lỗi khi xóa file"


@app.route('/download/<file_name>')
def download_file(file_name):
    # Nhận access_key, secret_key, kms_key_id từ form đăng nhập
    access_key = request.args.get('access_key')
    secret_key = request.args.get('secret_key')
    kms_key_id = request.args.get('kms_key_id')

    # Tạo client S3
    s3_client = create_s3_client(access_key, secret_key)

    # Tải về file từ S3
    response = s3_client.get_object(Bucket="your_bucket_name", Key=file_name)
    file_data = response['Body'].read()

    # Đặt loại MIME phù hợp cho file ảnh (ví dụ: image/png)
    mime_type = "image/png"  # Thay đổi loại MIME phù hợp với định dạng của file ảnh

    # Tạo phản hồi Flask với dữ liệu tệp và loại MIME
    flask_response = make_response(file_data)
    flask_response.headers["Content-Type"] = mime_type
    flask_response.headers["Content-Disposition"] = f"attachment; filename={file_name}"

    return flask_response


# Route cho thao tác chia sẻ tệp tin
@app.route('/share/<file_name>')
def share_file(file_name):
    # Nhận access_key, secret_key, kms_key_id từ form đăng nhập
    access_key = session.get('access_key')
    secret_key = session.get('secret_key')
    kms_key_id = session.get('kms_key_id')

    # Tạo client S3
    s3_client = create_s3_client(access_key, secret_key)

    # Tạo đường link chia sẻ
    shared_link = generate_shared_link(file_name, BUCKETNAME, s3_client)

    if shared_link:
        return render_template('share_file.html', shared_link=shared_link)
    else:
        return "Lỗi khi tạo đường link chia sẻ"


if __name__ == '__main__':
    app.run(debug=False)
