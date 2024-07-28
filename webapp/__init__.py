from flask import Flask
from webapp.routes import main
from webapp.extensions import talisman
from flask_sockets import Sockets

def load_key(filename):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return None

SECRET_KEY = load_key('webapp/secret_key.key')
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Настройка CSP для разрешения встроенных стилей и скриптов
csp = {
    'default-src': '\'self\'',
    'script-src': ['\'self\'', '\'unsafe-inline\''],
    'style-src': ['\'self\'', '\'unsafe-inline\''],
}

talisman.init_app(app, content_security_policy=csp)
app.register_blueprint(main)

sockets = Sockets(app)

import paramiko
import asyncio
from flask import request

@sockets.route('/ws/ssh')
def ssh_socket(ws):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Подключаемся к локальному SSH серверу (или укажите нужные параметры)
    ssh_client.connect(hostname="localhost", username="your_username", password="your_password")

    channel = ssh_client.invoke_shell()
    try:
        while not ws.closed:
            if ws.socket is not None:
                data = ws.receive()
                if data:
                    channel.send(data)
                if channel.recv_ready():
                    output = channel.recv(1024).decode('utf-8')
                    ws.send(output)
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        ssh_client.close()
        ws.close()
