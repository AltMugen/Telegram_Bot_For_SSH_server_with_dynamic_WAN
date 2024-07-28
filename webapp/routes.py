from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify, send_from_directory
from cryptography.fernet import Fernet
from config import FERNET_KEY, webapp_runtime_minutes
import time
import os

main = Blueprint('main', __name__)
cipher_suite = Fernet(FERNET_KEY)

def get_hashed_password():
    try:
        with open('webapp/hashed_password.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

@main.route('/', methods=['GET', 'POST'])
def index():
    hashed_password = get_hashed_password()
    if not hashed_password:
        return "Ошибка: Пароль не найден"

    if 'authenticated' in session:
        return redirect(url_for('main.choice'))
    if request.method == 'POST':
        password = request.form['password']
        if cipher_suite.decrypt(hashed_password.encode()).decode() == password:
            session['authenticated'] = True
            session['start_time'] = time.time()
            session['runtime'] = webapp_runtime_minutes * 60
            return redirect(url_for('main.choice'))
        else:
            flash('Invalid password')
    remaining_time = session.get('runtime', 0) - (time.time() - session.get('start_time', 0))
    return render_template('index.html', remaining_time=int(remaining_time))

@main.route('/choice', methods=['GET'])
def choice():
    if 'authenticated' not in session:
        return redirect(url_for('main.index'))
    remaining_time = session['runtime'] - (time.time() - session['start_time'])
    return render_template('choice.html', remaining_time=int(remaining_time))

@main.route('/ssh', methods=['GET', 'POST'])
def ssh():
    if 'authenticated' not in session:
        return redirect(url_for('main.index'))
    remaining_time = session['runtime'] - (time.time() - session['start_time'])
    return render_template('ssh.html', remaining_time=int(remaining_time))

@main.route('/ftp', methods=['GET', 'POST'])
def ftp():
    if 'authenticated' not in session:
        return redirect(url_for('main.index'))
    remaining_time = session['runtime'] - (time.time() - session['start_time'])
    return render_template('ftp.html', remaining_time=int(remaining_time))

# FTP API endpoints
@main.route('/ftp/api/get', methods=['GET'])
def ftp_get():
    path = request.args.get('path', '')
    abs_path = os.path.join('ftp_root', path)
    if not os.path.exists(abs_path):
        return jsonify(error='Path not found'), 404

    files = []
    for filename in os.listdir(abs_path):
        filepath = os.path.join(abs_path, filename)
        files.append({
            'name': filename,
            'is_dir': os.path.isdir(filepath),
            'size': os.path.getsize(filepath),
        })

    return jsonify(files=files)

@main.route('/ftp/api/upload', methods=['POST'])
def ftp_upload():
    path = request.form.get('path', '')
    abs_path = os.path.join('ftp_root', path)
    if not os.path.exists(abs_path):
        return jsonify(error='Path not found'), 404

    file = request.files['file']
    file.save(os.path.join(abs_path, file.filename))
    return jsonify(success=True)

@main.route('/ftp/api/createFolder', methods=['POST'])
def ftp_create_folder():
    path = request.form.get('path', '')
    abs_path = os.path.join('ftp_root', path)
    folder_name = request.form.get('folder_name', '')
    os.makedirs(os.path.join(abs_path, folder_name), exist_ok=True)
    return jsonify(success=True)

@main.route('/ftp/api/delete', methods=['POST'])
def ftp_delete():
    path = request.form.get('path', '')
    abs_path = os.path.join('ftp_root', path)
    if os.path.isdir(abs_path):
        os.rmdir(abs_path)
    else:
        os.remove(abs_path)
    return jsonify(success=True)
