from main import bot, dp
import os

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Command, Text
from config import admin_id, user

from menu import menu, common_commands


async def send_to_admin(dp):
    await bot.send_message(chat_id=admin_id, text="bot has been started")


async def shutdowning(dp):
    await bot.send_message(chat_id=admin_id, text="bot has been turned off")


@dp.message_handler(Text(startswith='$'))
async def terminal(message: Message):
    # text = 'usage:\n' + '$"[command]" > output.txt (optional)'
    # if message.text[0] == '$':
        # 'ssh komarov.na@calc.cod.phystech.edu "' + message.text[1:] + '" > output.txt'
    print('Command: ' + message.text[1:] + '\n')
    try:
        os.system(f'ssh {user} ' + message.text[1:])
        try:
            with open('output.txt', 'r') as f:
                text = f.read()
        except:
            text = 'output file cannot be read'
    except:
        text = f'command {message.text[1:]} was not executed'

    text = text_replace(text)

    await message.answer(text=text)


@dp.message_handler(Command("common"))
async def terminal_menu(message: Message):
    await message.answer(text='common commands', reply_markup=common_commands)


@dp.message_handler(Text(equals=["ls", "squeue", "sinfo"]))
async def actions(message: Message):
    command = message.text
    if message.text == "sinfo":
        command = "sinfo -p RT"
    try:
        os.system(f'ssh {user} "' + command + '" > output.txt')
        try:
            with open('output.txt', 'r') as f:
                text = f.read()
        except:
            text = 'output file cannot be read'
    except:
        text = f'command "{command}" was not executed'

    text = text_replace(text)

    await message.answer(text=text)

@dp.message_handler(Command("menu"))
async def calc_menu(message: Message):
    await message.answer(text='menu', reply_markup=menu)

@dp.message_handler(Text(equals=["Start computing", "Current state", "Terminate task"]))
async def actions_calc(message: Message):

    if message.text == "Start computing":
        print(message.text)
    if message.text == "Current state":
        print(message.text)
    if message.text == "Terminate task":
        print(message.text)
    '''
    try:
        os.system(f'ssh {user} "' + command + '" > output.txt')
        try:
            with open('output.txt', 'r') as f:
                text = f.read()
        except:
            text = 'output file cannot be read'
    except:
        text = f'command "{command}" was not executed' '''

    # text = text_replace(text)

    # await message.answer(text=text)



'''
@dp.message_handler(Command("menu"))
async def show_menu(message: Message):
    await message.answer(text="Menu is here:", reply_markup=menu)


@dp.message_handler(Text(equals=["Connect to cluster", "Kill a bot"]))
async def actions(message: Message):
    await message.answer(f"You have chosen {message.text}",
                         reply_markup=ReplyKeyboardRemove())
    
'''

def text_replace(text):

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

    return text
