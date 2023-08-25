from main import bot, dp
import os

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Command, Text
from config import admin_id

from menu import menu


async def send_to_admin(dp):
    await bot.send_message(chat_id=admin_id, text="bot has been started")

async def shutdowning(dp):
    await bot.send_message(chat_id=admin_id, text="bot has been turned off")


@dp.message_handler()
async def response(message: Message):
    text = 'usage:\n' + '$"[command]" > output.txt (optional)'
    if message.text[0] == '$':
        text = 'Command was: \n' + 'ssh komarov.na@calc.cod.phystech.edu ' + message.text[1:] + '\n'
        # 'ssh komarov.na@calc.cod.phystech.edu "' + message.text[1:] + '" > output.txt'
        print(text)
        try:
            os.system('ssh komarov.na@calc.cod.phystech.edu ' + message.text[1:])
            try:
                with open('output.txt', 'r') as f:
                    text = text + '\n' + f.read()
            except:
                text = text + '\n' + 'output file cannot be read'
        except:
            text = text + '\n' + 'command was not executed'

    if message.text == '':
        text = "?"

    text = text.replace('_', '\\_')
    text = text.replace('*', '\\*')
    text = text.replace('[', '\\[')
    text = text.replace(']', '\\]')
    text = text.replace('(', '\\(')
    text = text.replace(')', '\\)')
    text = text.replace('~', '\\~')
    text = text.replace('`', '\\`')
    text = text.replace('>', '\\>')
    text = text.replace('#', '\\#')
    text = text.replace('+', '\\+')
    text = text.replace('-', '\\-')
    text = text.replace('=', '\\=')
    text = text.replace('|', '\\|')
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')
    text = text.replace('.', '\\.')
    text = text.replace('!', '\\!')

    # print(text)

    await message.answer(text=text)

'''
@dp.message_handler(Command("menu"))
async def show_menu(message: Message):
    await message.answer(text="Menu is here:", reply_markup=menu)


@dp.message_handler(Text(equals=["Connect to cluster", "Kill a bot"]))
async def actions(message: Message):
    await message.answer(f"You have chosen {message.text}",
                         reply_markup=ReplyKeyboardRemove())
    
'''