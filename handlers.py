from main import bot, dp

from aiogram.types import Message
from config import admin_id


async def send_to_admin(dp):
    await bot.send_message(chat_id=admin_id, text="bot has been started")

async def shutdowning(dp):
    await bot.send_message(chat_id=admin_id, text="bot has been turned off")


@dp.message_handler()
async def response(message: Message):
    text = '?'
    if message.text == 'start computing':
        text = "computing has been started"
    if message.text == 'turn off':
        text = "No, I don`t want to be turned off"
    if message.text == 'terminate computing':
        text = "computing has been terminated"

    await message.answer(text=text)