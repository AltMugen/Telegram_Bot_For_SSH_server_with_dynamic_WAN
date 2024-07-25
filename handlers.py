from telebot import types
from config import *
from database import Database
from utils import get_external_ip, get_saved_wan_ip, save_wan_ip, setup_port_forwarding

db = Database('bot.db')


async def start_handler(bot, message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await auth_msg(bot, message)
        return

    await db.add_user(message.from_user.id)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    get_ip_btn = types.KeyboardButton('Получить IP')
    user_mgmt_btn = types.KeyboardButton('Управление пользователями')
    settings_btn = types.KeyboardButton('Дополнительные настройки')
    markup.add(get_ip_btn, user_mgmt_btn, settings_btn)
    await bot.send_message(message.chat.id, "Добро пожаловать! Ваши настройки сохранены.", reply_markup=markup)


async def handle_buttons(bot, message: types.Message):
    if not await db.user_exists(message.from_user.id):
        await auth_msg(bot, message)
        return

    if message.text == 'Получить IP':
        await get_ip_handler(bot, message)
    elif message.text == 'Управление пользователями':
        await manage_users_menu(bot, message)
    elif message.text == 'Добавить пользователя':
        await add_user_handler(bot, message)
    elif message.text == 'Удалить пользователя':
        await remove_user_handler(bot, message)
    elif message.text == 'Дополнительные настройки':
        await additional_settings_menu(bot, message)
    elif message.text == 'Назад':
        await start_handler(bot, message)


async def get_ip_handler(bot, message: types.Message):
    if not await db.user_exists(message.from_user.id):
        await auth_msg(bot, message)
        return

    current_wan_ip = await get_external_ip()
    saved_wan_ip = await get_saved_wan_ip()

    if current_wan_ip and current_wan_ip != saved_wan_ip:
        await setup_port_forwarding(local_ip, local_port, wan_port)
        await save_wan_ip(current_wan_ip)
        await bot.send_message(message.chat.id,
                               f"Ваш внешний IP адрес изменился: {current_wan_ip}. Порт был перенаправлен.")
    elif current_wan_ip:
        await bot.send_message(message.chat.id, f"Ваш внешний IP адрес: {current_wan_ip}.")
    else:
        await bot.send_message(message.chat.id, "Не удалось получить внешний IP адрес.")


async def add_user_handler(bot, message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await auth_msg(bot, message)
        return

    await bot.send_message(message.chat.id, "Введите ID пользователя для добавления:")
    bot.register_next_step_handler(message, process_add_user_step)


async def process_add_user_step(bot, message: types.Message):
    try:
        new_user_id = int(message.text)
        if await db.user_exists(new_user_id):
            await bot.send_message(message.chat.id, f"Пользователь {new_user_id} уже существует.")
        else:
            # Проверка существования пользователя в Telegram
            try:
                user = await bot.get_chat(new_user_id)
                await db.add_user(new_user_id)
                await bot.send_message(message.chat.id, f"Пользователь {new_user_id} ({user.username}) был добавлен.")
            except Exception as e:
                await bot.send_message(message.chat.id, f"Не удалось найти пользователя с ID {new_user_id} в Telegram.")
    except ValueError:
        await bot.send_message(message.chat.id, "Пожалуйста, введите корректный ID пользователя.")


async def manage_users_menu(bot, message: types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    add_user_btn = types.KeyboardButton('Добавить пользователя')
    remove_user_btn = types.KeyboardButton('Удалить пользователя')
    back_btn = types.KeyboardButton('Назад')
    markup.add(add_user_btn, remove_user_btn, back_btn)

    users = await db.get_all_users()
    users_list = '\n'.join(map(str, users)) if users else 'Нет пользователей'

    await bot.send_message(message.chat.id, f"Список пользователей:\n{users_list}", reply_markup=markup)


async def remove_user_handler(bot, message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await auth_msg(bot, message)
        return

    await bot.send_message(message.chat.id, "Введите ID пользователя для удаления:")
    bot.register_next_step_handler(message, process_remove_user_step)


async def process_remove_user_step(bot, message: types.Message):
    try:
        user_id = int(message.text)
        if await db.user_exists(user_id):
            await db.remove_user(user_id)
            await bot.send_message(message.chat.id, f"Пользователь {user_id} был удален.")
        else:
            await bot.send_message(message.chat.id, f"Пользователь с ID {user_id} не найден.")
    except ValueError:
        await bot.send_message(message.chat.id, "Пожалуйста, введите корректный ID пользователя.")


async def additional_settings_menu(bot, message: types.Message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    force_forward_btn = types.KeyboardButton('Принудительно пробросить порт')
    back_btn = types.KeyboardButton('Назад')
    markup.add(force_forward_btn, back_btn)
    await bot.send_message(message.chat.id, "Дополнительные настройки:", reply_markup=markup)


async def force_port_forwarding_handler(bot, message: types.Message):
    await setup_port_forwarding(local_ip, local_port, wan_port)  # замените на ваши значения
    await bot.send_message(message.chat.id, "Порт был принудительно перенаправлен.")


async def auth_msg(bot, message: types.Message):
    await bot.send_message(message.chat.id, "Вы не авторизованы для использования этого бота.")
