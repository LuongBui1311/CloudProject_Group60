from flask import Flask, render_template, request, redirect, url_for, send_file, session, make_response
import boto3
from botocore.client import Config
import delete
import share
import upload
import time
import load
import uploadfile
from flask import Flask, jsonify
import create_client

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

        # Store data in the session
        session['access_key'] = access_key
        session['secret_key'] = secret_key
        session['kms_key_id'] = kms_key_id
        return redirect(url_for('file_list'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    access_key = session.get('access_key')
    secret_key = session.get('secret_key')
    kms_key_id = session.get('kms_key_id')

    session.pop('access_key', None)
    session.pop('secret_key', None)
    session.pop('kms_key_id', None)

    return redirect(url_for('login'))


@app.route('/files', methods=['GET', 'POST'])
def file_list():
    access_key = session.get('access_key')
    secret_key = session.get('secret_key')
    kms_key_id = session.get('kms_key_id')
    mess = request.args.get("mess")
    error = request.args.get("error")
    time = request.args.get("time")

    s3_client = create_client.create_s3_client(access_key, secret_key)

    files = load.read_all_files_from_s3(BUCKETNAME, s3_client)

    return render_template('file_list.html', files=files,
                           access_key=access_key, secret_key=secret_key, 
                           kms_key_id=kms_key_id, s3_client=s3_client, 
                           mess = mess, error = error, time = time)


# Route cho thao tác upload tệp tin

@app.route('/files/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        start_time = time.time()
        access_key = session.get('access_key')
        secret_key = session.get('secret_key')
        mess = ""
        error = ""
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                message = uploadfile.upload_file_to_s3(file, access_key, secret_key, BUCKETNAME)
                if message != "":
                    mess = "Upload thành công !"
                    end_time = time.time()
                    upload_time = end_time - start_time
                    return redirect(url_for('file_list', time=upload_time ,mess = mess, error = error))
                else:
                    print('Upload error!!!')
                    status = 'False'
                    return jsonify({'status': status, 'message': 'Failed to upload file'})
        return "Không có file được chọn"
    return render_template('upload_file.html')

# @app.route('/files/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         # khởi tạo thời gian đầu
#         start_time = time.time()

#         # # Retrieve data from the session
#         access_key = session.get('access_key')
#         secret_key = session.get('secret_key')
#         kms_key_id = session.get('kms_key_id')
#         mess = ""
#         error = ""
#         # # Tạo client S3
#         s3_client = create_client.create_s3_client(access_key, secret_key)
#         #
#         # # Upload file
#         if 'file' in request.files:
#             file = request.files['file']
#             if file.filename != '':
#                 # Lưu file tạm thời và upload lên S3
#                 file_path = f"{file.filename}"
#                 file.save(file_path)
#                 if upload.upload_file_to_s3(file_path, BUCKETNAME, s3_client, kms_key_id):
#                     mess = "Upload thành công !"
#                     # Khởi tạo thời gian kết thúc
#                     end_time = time.time()
#                     # tính thời gian bằng cách trừ tg đầu và tg kết
#                     upload_time = end_time - start_time
#                     # chuyển thời gian tính qua html
#                     return redirect(url_for('file_list', time=upload_time ,mess = mess, error = error))
#                 else:
#                     return "Lỗi khi upload file"

#         return "Không có file được chọn"

#     return render_template('upload_file.html')

# Route cho thao tác xóa tệp tin
@app.route('/delete/<file_name>')
def delete_file(file_name):

    start_time = time.time()
    access_key = request.args.get('access_key')
    secret_key = request.args.get('secret_key')
    kms_key_id = request.args.get('kms_key_id')
    mess = ""
    error = ""
    # Tạo client S3
    s3_client = create_client.create_s3_client(access_key, secret_key)

    try:
        if delete.delete_file_from_s3(file_name, BUCKETNAME, s3_client):
            mess = "Xóa thành công!"
            end_time = time.time()
            delete_time = end_time - start_time
        else:
            error = "Xóa thất bại !"
    except Exception as e:
        error = e
        
    return redirect(url_for('file_list', access_key=access_key, time=delete_time,
                                secret_key=secret_key, kms_key_id=kms_key_id, 
                                mess = mess, error=error))


@app.route('/download/<file_name>')
def download_file(file_name):
    start_time = time.time()
    access_key = request.args.get('access_key')
    secret_key = request.args.get('secret_key')
    kms_key_id = request.args.get('kms_key_id')
    mess = ""
    error = ""
    try:
        s3_resource = create_client.create_s3_resource(access_key, secret_key)
        
        s3_bucket = s3_resource.Bucket(BUCKETNAME)
        for s3_file in s3_bucket.objects.all():
            if s3_file.key == file_name:
                s3_resource.Bucket(BUCKETNAME).download_file(s3_file.key, file_name)
                end_time = time.time()
                download_time = end_time - start_time
                mess = "Tải về thành công !"
    except Exception as e:
        error = "Tải về thất bại!"

    return redirect(url_for('file_list',time=download_time, 
                            access_key=access_key, secret_key=secret_key, kms_key_id=kms_key_id,
                            mess = mess, error = error))
    
# Route cho thao tác chia sẻ tệp tin
@app.route('/share/<file_name>')
def share_file(file_name):
    start_time = time.time()
    access_key = session.get('access_key')
    secret_key = session.get('secret_key')
    kms_key_id = session.get('kms_key_id')
    mess = ""
    error = ""
    mytime = time.time()

    s3_client = create_client.create_s3_client(access_key, secret_key)

    shared_link = share.generate_shared_link(access_key, BUCKETNAME, secret_key, file_name)

    if shared_link:
        end_time = time.time()
        share_time = end_time - start_time
        mytime = share_time
        mess = "Tạo đường dẫn thành công !"
    else:
        error = "Tạo đường dẫn thất bại !"
    
    return render_template('share_file.html', shared_link=shared_link, share_time=share_time, 
                               mess = mess, error = error, time = mytime)

if __name__ == '__main__':
    app.run(debug=False)
