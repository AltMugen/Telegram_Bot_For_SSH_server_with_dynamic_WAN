import asyncio
from telebot.async_telebot import AsyncTeleBot
from config import *
from handlers import start_handler, get_ip_handler, add_user_handler
from database import Database

bot = AsyncTeleBot(API_TOKEN)
db = Database('bot.db')

@bot.message_handler(commands=['start'])
async def start(message):
    await start_handler(bot, message)

@bot.message_handler(commands=['get_ip'])
async def get_ip(message):
    await get_ip_handler(bot, message)

@bot.message_handler(commands=['add_user'])
async def add_user(message):
    await add_user_handler(bot, message)

async def on_startup():
    await db.init_db()
    await bot.send_message(chat_id=int(ADMIN_ID), text='Bot started!')

async def main():
    await on_startup()
    await bot.polling()

if __name__ == '__main__':
    asyncio.run(main())

