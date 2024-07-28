# config.py
import os
import time
import base64

# Локальный IP устройства
local_ip = ""
# Открытый ssh порт
local_port =
# Порт на который идёт переброс
wan_port =
# Имя пользователя на сервере
username = ""

# Bot token
API_TOKEN = ""

# Название базы данных для хранения настроек
DB_NAME = 'bot.db'

# ID пользователя администратора бота(id телеграм можно взять у https://t.me/username_to_id_bot)
ADMIN_ID = ''

# Текст - уведомление что пользователь не имеет прав для пользования этим ботом
error_auth = "У вас нет прав на пользование этим ботом!"

# Файл с предыдущим WAN
WAN_IP_FILE = ''

# Заброшеный код для WEBAPP
# Ключ для хеширования
# initial_password =b"123"
#
# # Параметры для веб-приложения
# webapp_local_port = 7686
# webapp_wan_port = 6786
# webapp_runtime_minutes = 60  # Время работы веб-приложения в минутах
#
# # Ключи для шифрования
# def save_key(key, filename):
#     with open(filename, 'wb') as f:
#         f.write(key)
#
# def load_key(filename):
#     try:
#         with open(filename, 'rb') as f:
#             return f.read()
#     except FileNotFoundError:
#         return None
#
# def save_timestamp(filename):
#     with open(filename, 'w') as f:
#         f.write(str(time.time()))
#
# def load_timestamp(filename):
#     try:
#         with open(filename, 'r') as f:
#             return float(f.read())
#     except FileNotFoundError:
#         return 0
#
# def check_and_update_keys():
#     timestamp_file = 'webapp/last_update_timestamp.txt'
#     last_update = load_timestamp(timestamp_file)
#     current_time = time.time()
#     if current_time - last_update > 24 * 3600:
#         # Обновление секретного ключа и ключа шифрования
#         SECRET_KEY = os.urandom(32)
#         save_key(SECRET_KEY, 'webapp/secret_key.key')
#
#         FERNET_KEY = base64.urlsafe_b64encode(os.urandom(32))
#         save_key(FERNET_KEY, 'webapp/fernet_key.key')
#
#         # Обновление метки времени
#         save_timestamp(timestamp_file)
#
# # Проверка и обновление ключей, если прошло больше 24 часов
# check_and_update_keys()
#
# # Загрузка секретного ключа и ключа шифрования
# SECRET_KEY = load_key('webapp/secret_key.key')
# FERNET_KEY = load_key('webapp/fernet_key.key')
