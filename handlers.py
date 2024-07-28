# import subprocess
# import asyncio
# import random
# import string
from telebot import types
from config import *
from database import Database
from utils import get_external_ip, get_saved_wan_ip, save_wan_ip, setup_port_forwarding
# from cryptography.fernet import Fernet

db = Database('bot.db')

# cipher_suite = Fernet(FERNET_KEY)
session_start_time = None
bot_messages = {}
next_step_handlers = {}
async def delete_last_bot_messages(bot, chat_id):
    if chat_id in bot_messages:
        for message_id in bot_messages[chat_id]:
            try:
                await bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                print(f"Failed to delete message {message_id}: {e}")
        bot_messages[chat_id] = []

async def save_bot_message(chat_id, message):
    if chat_id not in bot_messages:
        bot_messages[chat_id] = []
    bot_messages[chat_id].append(message.message_id)

async def start_handler(bot, message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await auth_msg(bot, message)
        return

    await db.add_user(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    get_ip_btn = types.KeyboardButton('🔹 Получить IP 🔹')
    user_mgmt_btn = types.KeyboardButton('👥 Управление пользователями 👥')
    settings_btn = types.KeyboardButton('⚠️ Дополнительные настройки ⚠️')
    markup.add(get_ip_btn, user_mgmt_btn, settings_btn)
    sent_message = await bot.send_message(message.chat.id, "🫧Основное меню🫧", reply_markup=markup)

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        print(f"Failed to delete user message {message.message_id}: {e}")
    await delete_last_bot_messages(bot, message.chat.id)
    await save_bot_message(message.chat.id, sent_message)


async def handle_buttons(bot, message: types.Message):
    if not await db.user_exists(message.from_user.id):
        await auth_msg(bot, message)
        return
    if message.chat.id in next_step_handlers:
        await next_step_handlers[message.chat.id](bot, message)
    elif message.text == '🔹 Получить IP 🔹':
        await get_ip_handler(bot, message)
    elif message.text == '👥 Управление пользователями 👥':
        await manage_users_menu(bot, message)
    elif message.text == '🟢 Добавить пользователя 🟢':
        await add_user_handler(bot, message)
    elif message.text == '🔴 Удалить пользователя 🔴':
        await remove_user_handler(bot, message)
    elif message.text == '⚠️ Дополнительные настройки ⚠️':
        await additional_settings_menu(bot, message)
    # elif message.text == '❌ WEB-APP ssh/ftp ❌':
    #     await webapp_ssh_ftp_handler(bot, message)
    elif message.text == '🍀 Принудительно пробросить порт 🍀':
        await force_port_forwarding_handler(bot, message)
    elif message.text == '🔺 Назад 🔺':
        await start_handler(bot, message)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Функция не дописана, проблемы: настройка сертификатов(самоподписные не подходят), ssh/ftp  доступ не настроенны и не тестировались (настройка происходит не из конфига) #
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# async def webapp_ssh_ftp_handler(bot, message: types.Message):
#     print("Handling WEB-APP ssh/ftp")
    # global session_start_time, hashed_password
    #
    # if message.from_user.id != int(ADMIN_ID):
    #     await auth_msg(bot, message)
    #     return
    #
    # waiting_message = await bot.send_message(message.chat.id, "Терпение, это может занять некоторое время...")
    # await save_bot_message(message.chat.id, waiting_message)
    #
    # markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    # get_ip_btn = types.KeyboardButton('🔹 Получить IP 🔹')
    # user_mgmt_btn = types.KeyboardButton('👥 Управление пользователями 👥')
    # settings_btn = types.KeyboardButton('⚠️ Дополнительные настройки ⚠️')
    # markup.add(get_ip_btn, user_mgmt_btn, settings_btn)
    #
    # if session_start_time and (asyncio.get_event_loop().time() - session_start_time < webapp_runtime_minutes * 60):
    #     external_ip = await get_external_ip()
    #     decrypted_password = cipher_suite.decrypt(hashed_password.encode()).decode()
    #     try:
    #         sent_message = await bot.edit_message_text(chat_id=message.chat.id, message_id=waiting_message.message_id,
    #                                                    text=f"Веб-приложение уже запущено.\nIP: `{external_ip}:{webapp_wan_port}`\nПароль: `{decrypted_password}`",
    #                                                    reply_markup=markup, parse_mode='Markdown')
    #         await delete_last_bot_messages(bot, message.chat.id)
    #         await save_bot_message(message.chat.id, sent_message)
    #     except Exception as e:
    #         sent_message = await bot.send_message(message.chat.id,
    #                                               f"Веб-приложение уже запущено.\nIP: `{external_ip}:{webapp_wan_port}`\nПароль: `{decrypted_password}`",
    #                                               reply_markup=markup, parse_mode='Markdown')
    #         await delete_last_bot_messages(bot, message.chat.id)
    #         await save_bot_message(message.chat.id, sent_message)
    #     try:
    #         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    #     except Exception as e:
    #         print(f"Failed to delete user message {message.message_id}: {e}")
    #     return
    #
    # # Проброс порта
    # await setup_port_forwarding(local_ip, webapp_local_port, webapp_wan_port)
    #
    # # Генерация нового пароля
    # new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    # encrypted_password = cipher_suite.encrypt(new_password.encode()).decode()
    #
    # # Сохранение нового пароля в переменной hashed_password и запись времени начала сессии
    # hashed_password = encrypted_password
    # session_start_time = asyncio.get_event_loop().time()
    #
    # # Запись пароля в файл
    # with open('webapp/hashed_password.txt', 'w') as f:
    #     f.write(hashed_password)
    #
    # external_ip = await get_external_ip()
    # try:
    #     sent_message = await bot.edit_message_text(chat_id=message.chat.id, message_id=waiting_message.message_id,
    #                                                text=f"Веб-приложение будет доступно на порту {webapp_wan_port} в течение {webapp_runtime_minutes} минут.\nIP: `{external_ip}:{webapp_wan_port}`\nПароль: `{new_password}`",
    #                                                reply_markup=markup, parse_mode='Markdown')
    #     await delete_last_bot_messages(bot, message.chat.id)
    #     await save_bot_message(message.chat.id, sent_message)
    # except Exception as e:
    #     sent_message = await bot.send_message(message.chat.id,
    #                                           f"Веб-приложение будет доступно на порту {webapp_wan_port} в течение {webapp_runtime_minutes} минут.\nIP: `{external_ip}:{webapp_wan_port}`\nПароль: `{new_password}`",
    #                                           reply_markup=markup, parse_mode='Markdown')
    #     await delete_last_bot_messages(bot, message.chat.id)
    #     await save_bot_message(message.chat.id, sent_message)
    #
    # # Запуск веб-приложения
    # process = subprocess.Popen(["python", "path_to_your_webapp.py"])
    #
    # # Остановка веб-приложения по истечении времени
    # await asyncio.sleep(webapp_runtime_minutes * 60)
    # process.terminate()
    # sent_message = await bot.send_message(message.chat.id, "Веб-приложение остановлено.", reply_markup=markup)
    # await save_bot_message(message.chat.id, sent_message)
    # try:
    #     await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    # except Exception as e:
    #     print(f"Failed to delete user message {message.message_id}: {e}")

async def get_ip_handler(bot, message: types.Message):
    if not await db.user_exists(message.from_user.id):
        await auth_msg(bot, message)
        return

    waiting_message = await bot.send_message(message.chat.id, "Получение IP адреса...")
    await save_bot_message(message.chat.id, waiting_message)

    current_wan_ip = await get_external_ip()
    saved_wan_ip = await get_saved_wan_ip()

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    get_ip_btn = types.KeyboardButton('🔹 Получить IP 🔹')
    user_mgmt_btn = types.KeyboardButton('👥 Управление пользователями 👥')
    settings_btn = types.KeyboardButton('⚠️ Дополнительные настройки ⚠️')
    markup.add(get_ip_btn, user_mgmt_btn, settings_btn)

    if current_wan_ip and current_wan_ip != saved_wan_ip:
        await setup_port_forwarding(local_ip, local_port, wan_port)
        await save_wan_ip(current_wan_ip)
        try:
            sent_message = await bot.edit_message_text(chat_id=message.chat.id, message_id=waiting_message.message_id,
                                                       text=f"Ваш внешний IP адрес изменился, порт перенаправлен: `{current_wan_ip}:{wan_port}`\n```ssh ssh -p {wan_port} {username}@{current_wan_ip}```",
                                                       reply_markup=markup, parse_mode='Markdown')
            await delete_last_bot_messages(bot, message.chat.id)
            await save_bot_message(message.chat.id, sent_message)
        except Exception as e:
            sent_message = await bot.send_message(message.chat.id,
                                                  f"Ваш внешний IP адрес изменился, порт перенаправлен: `{current_wan_ip}:{wan_port}`\n```ssh ssh -p {wan_port} {username}@{current_wan_ip}```",
                                                  reply_markup=markup, parse_mode='Markdown')
            await delete_last_bot_messages(bot, message.chat.id)
            await save_bot_message(message.chat.id, sent_message)
    elif current_wan_ip:
        try:
            sent_message = await bot.edit_message_text(chat_id=message.chat.id, message_id=waiting_message.message_id,
                                                       text=f"Ваш внешний IP адрес: `{current_wan_ip}:{wan_port}`\n```ssh ssh -p {wan_port} {username}@{current_wan_ip}```",
                                                       reply_markup=markup, parse_mode='Markdown')
            await delete_last_bot_messages(bot, message.chat.id)
            await save_bot_message(message.chat.id, sent_message)
        except Exception as e:
            sent_message = await bot.send_message(message.chat.id,
                                                  f"Ваш внешний IP адрес: `{current_wan_ip}:{wan_port}`\n```ssh ssh -p {wan_port} {username}@{current_wan_ip}```",
                                                  reply_markup=markup, parse_mode='Markdown')
            await delete_last_bot_messages(bot, message.chat.id)
            await save_bot_message(message.chat.id, sent_message)
    else:
        try:
            sent_message = await bot.edit_message_text(chat_id=message.chat.id, message_id=waiting_message.message_id,
                                                       text="Не удалось получить внешний IP адрес.", reply_markup=markup)
            await delete_last_bot_messages(bot, message.chat.id)
            await save_bot_message(message.chat.id, sent_message)
        except Exception as e:
            sent_message = await bot.send_message(message.chat.id, "Не удалось получить внешний IP адрес.", reply_markup=markup)
            await delete_last_bot_messages(bot, message.chat.id)
            await save_bot_message(message.chat.id, sent_message)

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        print(f"Failed to delete user message {message.message_id}: {e}")


async def add_user_handler(bot, message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await auth_msg(bot, message)
        return

    waiting_message = await bot.send_message(message.chat.id, "Введите ID пользователя для добавления:")
    await save_bot_message(message.chat.id, waiting_message)

    next_step_handlers[message.chat.id] = process_add_user_step

async def process_add_user_step(bot, message: types.Message):
    if message.chat.id not in next_step_handlers or next_step_handlers[message.chat.id] != process_add_user_step:
        return

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    add_user_btn = types.KeyboardButton('🟢 Добавить пользователя 🟢')
    remove_user_btn = types.KeyboardButton('🔴 Удалить пользователя 🔴')
    back_btn = types.KeyboardButton('🔺 Назад 🔺')
    markup.add(add_user_btn, remove_user_btn, back_btn)

    try:
        new_user_id = int(message.text)
        if await db.user_exists(new_user_id):
            sent_message = await bot.send_message(message.chat.id, f"Пользователь {new_user_id} уже существует.", reply_markup=markup)
        else:
            try:
                user = await bot.get_chat(new_user_id)
                await db.add_user(new_user_id)
                sent_message = await bot.send_message(message.chat.id, f"Пользователь {new_user_id} ({user.username}) был добавлен.", reply_markup=markup)
            except Exception as e:
                sent_message = await bot.send_message(message.chat.id, f"Не удалось найти пользователя с ID {new_user_id} в Telegram.", reply_markup=markup)
    except ValueError:
        sent_message = await bot.send_message(message.chat.id, "Пожалуйста, введите корректный ID пользователя.", reply_markup=markup)

    await delete_last_bot_messages(bot, message.chat.id)
    await save_bot_message(message.chat.id, sent_message)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        print(f"Failed to delete user message {message.message_id}: {e}")

    # Удаляем обработчик после выполнения
    del next_step_handlers[message.chat.id]
async def manage_users_menu(bot, message: types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    add_user_btn = types.KeyboardButton('🟢 Добавить пользователя 🟢')
    remove_user_btn = types.KeyboardButton('🔴 Удалить пользователя 🔴')
    back_btn = types.KeyboardButton('🔺 Назад 🔺')
    markup.add(add_user_btn, remove_user_btn, back_btn)

    users = await db.get_all_users()
    users_list = '\n'.join(map(str, users)) if users else 'Нет пользователей'

    sent_message = await bot.send_message(message.chat.id, f"Список пользователей:\n{users_list}", reply_markup=markup)
    await delete_last_bot_messages(bot, message.chat.id)
    await save_bot_message(message.chat.id, sent_message)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        print(f"Failed to delete user message {message.message_id}: {e}")


async def remove_user_handler(bot, message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await auth_msg(bot, message)
        return

    waiting_message = await bot.send_message(message.chat.id, "Введите ID пользователя для удаления:")
    await save_bot_message(message.chat.id, waiting_message)

    next_step_handlers[message.chat.id] = process_remove_user_step

async def process_remove_user_step(bot, message: types.Message):
    if message.chat.id not in next_step_handlers or next_step_handlers[message.chat.id] != process_remove_user_step:
        return

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    add_user_btn = types.KeyboardButton('🟢 Добавить пользователя 🟢')
    remove_user_btn = types.KeyboardButton('🔴 Удалить пользователя 🔴')
    back_btn = types.KeyboardButton('🔺 Назад 🔺')
    markup.add(add_user_btn, remove_user_btn, back_btn)

    try:
        user_id = int(message.text)
        if await db.user_exists(user_id):
            await db.remove_user(user_id)
            sent_message = await bot.send_message(message.chat.id, f"Пользователь {user_id} был удален.", reply_markup=markup)
        else:
            sent_message = await bot.send_message(message.chat.id, f"Пользователь с ID {user_id} не найден.", reply_markup=markup)
    except ValueError:
        sent_message = await bot.send_message(message.chat.id, "Пожалуйста, введите корректный ID пользователя.", reply_markup=markup)

    await delete_last_bot_messages(bot, message.chat.id)
    await save_bot_message(message.chat.id, sent_message)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        print(f"Failed to delete user message {message.message_id}: {e}")

    # Удаляем обработчик после выполнения
    del next_step_handlers[message.chat.id]
async def additional_settings_menu(bot, message: types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    force_forward_btn = types.KeyboardButton('🍀 Принудительно пробросить порт 🍀')
    webapp_btn = types.KeyboardButton('❌ WEB-APP ssh/ftp ❌')
    back_btn = types.KeyboardButton('🔺 Назад 🔺')
    markup.add(force_forward_btn, back_btn) #webapp_btn,
    sent_message = await bot.send_message(message.chat.id, "🫧Дополнительные настройки🫧", reply_markup=markup)
    await delete_last_bot_messages(bot, message.chat.id)
    await save_bot_message(message.chat.id, sent_message)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        print(f"Failed to delete user message {message.message_id}: {e}")

async def force_port_forwarding_handler(bot, message: types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    waiting_message = await bot.send_message(message.chat.id, "Получение IP адреса...")
    await save_bot_message(message.chat.id, waiting_message)

    force_forward_btn = types.KeyboardButton('🍀 Принудительно пробросить порт 🍀')
    webapp_btn = types.KeyboardButton('❌ WEB-APP ssh/ftp ❌')
    back_btn = types.KeyboardButton('🔺 Назад 🔺')
    markup.add(force_forward_btn, back_btn) #webapp_btn,

    await setup_port_forwarding(local_ip, local_port, wan_port)
    current_wan_ip = await get_external_ip()

    sent_message = await bot.send_message(message.chat.id, f"Порт был принудительно перенаправлен на IP: `{current_wan_ip}:{wan_port}`\n```ssh ssh -p {wan_port} {username}@{current_wan_ip}```", parse_mode='Markdown', reply_markup=markup)
    await delete_last_bot_messages(bot, message.chat.id)
    await save_bot_message(message.chat.id, sent_message)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        print(f"Failed to delete user message {message.message_id}: {e}")

# async def get_token_handler(bot, message: types.Message):
#     if message.from_user.id != int(ADMIN_ID):
#         await auth_msg(bot, message)
#         return
#
#     new_token = Fernet.generate_key().decode()
#     sent_message = await bot.send_message(message.chat.id, f"Ваш токен для доступа: {new_token}", reply_markup=types.ReplyKeyboardRemove())
#     await delete_last_bot_messages(bot, message.chat.id)
#     await save_bot_message(message.chat.id, sent_message)
#     try:
#         await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
#     except Exception as e:
#         print(f"Failed to delete user message {message.message_id}: {e}")

async def auth_msg(bot, message: types.Message):
    print(f"Handling unauthorized access from {message.from_user.id}")
    sent_message = await bot.send_message(message.chat.id, "Вы не авторизованы для использования этого бота.", reply_markup=types.ReplyKeyboardRemove())
    await delete_last_bot_messages(bot, message.chat.id)
    await save_bot_message(message.chat.id, sent_message)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        print(f"Failed to delete user message {message.message_id}: {e}")
