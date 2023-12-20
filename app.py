from flask import Flask, render_template, request, redirect, url_for, send_file, session, make_response
import boto3
from botocore.client import Config
import delete
import share
import upload
import time
import load
import create_client
#import mimetypes

app = Flask(__name__, static_folder='static')
app.secret_key = 'DQ0oU97ZLZyo4Jzd2duUsvgZ76P3SzLYHeWueykN' 

# Constants
NUM_BYTES_FOR_LEN = 4
BUCKETNAME = "endsemproject"

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
    s3_client = create_client.create_s3_client(access_key, secret_key)

    # Đọc danh sách tệp tin từ S3
    files = load.read_all_files_from_s3(BUCKETNAME, s3_client)

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
        start_time = time.time()

        # # Retrieve data from the session
        access_key = session.get('access_key')
        secret_key = session.get('secret_key')
        kms_key_id = session.get('kms_key_id')

        # if 'access_key' in session:
        #     access_key = session['access_key']
        #     return f"<h1>{access_key}</h1>"
        # return "abc"

        # # Tạo client S3
        s3_client = create_client.create_s3_client(access_key, secret_key)
        #
        # # Upload file
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Lưu file tạm thời và upload lên S3
                file_path = f"{file.filename}"
                file.save(file_path)
                if upload.upload_file_to_s3(file_path, BUCKETNAME, s3_client, kms_key_id):
                    end_time = time.time()
                    upload_time = end_time - start_time
                    print(f"Thời gian tải lên: {upload_time} giây")
                    return redirect(url_for('file_list') )
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
    s3_client = create_client.create_s3_client(access_key, secret_key)

    # Xóa file từ S3
    if delete.delete_file_from_s3(file_name, BUCKETNAME, s3_client):
        return redirect(url_for('file_list', access_key=access_key, secret_key=secret_key, kms_key_id=kms_key_id))
    else:
        return "Lỗi khi xóa file"


@app.route('/download/<file_name>')
def download_file(file_name):
    # khai báo thời gian thực ban đầu
    start_time = time.time()
    # Nhận access_key, secret_key, kms_key_id từ form đăng nhập
    access_key = request.args.get('access_key')
    secret_key = request.args.get('secret_key')
    kms_key_id = request.args.get('kms_key_id')

    s3_resource = create_client.create_s3_resource(access_key, secret_key)
    
    s3_bucket = s3_resource.Bucket(BUCKETNAME)
    for s3_file in s3_bucket.objects.all():
        if s3_file.key == file_name:
            s3_resource.Bucket(BUCKETNAME).download_file(s3_file.key, file_name)
            # Thời gian kết thúc tải file
            end_time = time.time()
            download_time = end_time - start_time

            print(f"Thời gian tải về: {download_time} giây")
    return redirect(url_for('file_list', access_key=access_key, secret_key=secret_key, kms_key_id=kms_key_id))
    
# Route cho thao tác chia sẻ tệp tin
@app.route('/share/<file_name>')
def share_file(file_name):
    # Nhận access_key, secret_key, kms_key_id từ form đăng nhập
    access_key = session.get('access_key')
    secret_key = session.get('secret_key')
    kms_key_id = session.get('kms_key_id')

    # Tạo client S3
    s3_client = create_client.create_s3_client(access_key, secret_key)

    # Tạo đường link chia sẻ
    shared_link = share.generate_shared_link(access_key, BUCKETNAME, secret_key, file_name)

    if shared_link:
        return render_template('share_file.html', shared_link=shared_link)
    else:
        return "Lỗi khi tạo đường link chia sẻ"


if __name__ == '__main__':
    app.run(debug=False)
