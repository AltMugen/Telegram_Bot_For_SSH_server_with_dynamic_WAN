import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from config import API_TOKEN, ADMIN_ID
from handlers import (
    start_handler, handle_buttons, add_user_handler, remove_user_handler, force_port_forwarding_handler
)
from database import Database

bot = AsyncTeleBot(API_TOKEN)
db = Database('bot.db')

@bot.message_handler(commands=['start'])
async def start(message):
    await start_handler(bot, message)
#
# @bot.message_handler(commands=['add_user'])
# async def add_user(message):
#     await add_user_handler(bot, message)
#
# @bot.message_handler(commands=['remove_user'])
# async def remove_user(message):
#     await remove_user_handler(bot, message)
#
# @bot.message_handler(commands=['force_forward'])
# async def force_forward(message):
#     await force_port_forwarding_handler(bot, message)

@bot.message_handler(func=lambda message: True, content_types=['text'])
async def handle_message(message):
    await handle_buttons(bot, message)

async def on_startup():
    await db.init_db()
    # await bot.send_message(chat_id=int(ADMIN_ID), text='Бот снова онлайн!')

async def main():
    await on_startup()
    await bot.polling()

if __name__ == '__main__':
    asyncio.run(main())
