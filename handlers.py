from telebot import types
from config import ADMIN_ID
from database import Database
from utils import get_external_ip

db = Database('bot.db')

async def start_handler(bot, message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await auth_msg(bot, message)
        return

    await db.add_user(message.from_user.id)
    await bot.send_message(message.chat.id, "Welcome! Your settings have been saved.")

async def get_ip_handler(bot, message: types.Message):
    if not await db.user_exists(message.from_user.id):
        await auth_msg(bot, message)
        return

    external_ip = await get_external_ip()
    if external_ip:
        await bot.send_message(message.chat.id, f"Your external IP address is: {external_ip}")
    else:
        await bot.send_message(message.chat.id, "Could not retrieve external IP address.")

async def add_user_handler(bot, message: types.Message):
    if message.from_user.id != int(ADMIN_ID):
        await auth_msg(bot, message)
        return

    try:
        new_user_id = int(message.text.split()[1])
        await db.add_user(new_user_id)
        await bot.send_message(message.chat.id, f"User {new_user_id} has been added.")
    except (IndexError, ValueError):
        await bot.send_message(message.chat.id, "Usage: /add_user <user_id>")

async def auth_msg(bot, message: types.Message):
    await bot.send_message(message.chat.id, "You are not authorized to use this bot.")
