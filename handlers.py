import asyncio

from main import bot, dp, computer, loop
import os

from threading import Thread
from time import sleep

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Command, Text
from config import admin_id, user

from menu import menu, common_commands


async def send_to_admin(dp):
    print('started')
    await bot.send_message(chat_id=admin_id, text="bot has been started")


async def shutdowning(dp):
    computer.check_curr_job_state()
    computer.save_to_file()
    await bot.send_message(chat_id=admin_id, text="bot has been turned off")


@dp.message_handler(Text(equals=['?']))
async def help(message: Message):
    await message.answer(text='usage:\n' + '$[command]')


@dp.message_handler(Text(startswith='$'))
async def terminal(message: Message):
    print('Command: ' + message.text[1:] + '\n')
    try:
        os.system(f'ssh {user} "' + message.text[1:] + '" > output.txt')
        try:
            with open('output.txt', 'r') as f:
                text = f.read()
        except:
            text = 'output file cannot be read'
    except:
        text = f'command {message.text[1:]} was not executed'

    text = text_replace(text)
    await message.answer(text=text)


@dp.message_handler(Text(startswith="/input: "))
async def set_input(message: Message):
    computer.input_dir = message.text[8:]
    computer.save_to_file()
    await message.answer(text=text_replace(f'input dir changed to: {computer.input_dir}'))


@dp.message_handler(Text(startswith="/output: "))
async def set_output(message: Message):
    computer.output_dir = message.text[9:]
    computer.save_to_file()
    await message.answer(text=text_replace(f'output dir changed to: {computer.output_dir}'))


@dp.message_handler(Command("common"))
async def terminal_menu(message: Message):
    await message.answer(text='common commands', reply_markup=common_commands)


@dp.message_handler(Text(equals=["ls", "squeue", "sinfo", "last file"]))
async def actions(message: Message):
    command = message.text
    if message.text == "sinfo":
        command = "sinfo -p RT"
    if message.text == "last file":
        command = 'ls -1rt | tail -n1'
    print('Command: ' + command + '\n')
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


@dp.message_handler(Text(startswith="/stage: "))
async def set_stage(message: Message):
    computer.curr_stage = int(message.text[8:])
    for i in computer.stages:
        if i < computer.curr_stage:
            computer.stages[i] = True
        else:
            computer.stages[i] = False
    computer.job_num = ''
    print(f'curr stage changed to {computer.curr_stage}')
    computer.save_to_file()
    await message.answer(text=text_replace(f'curr stage changed to {computer.curr_stage}'))


@dp.message_handler(Command("menu"))
async def calc_menu(message: Message):
    await message.answer(text='menu', reply_markup=menu)


@dp.message_handler(Text(equals=["Start computing", "Curr state", "Stages", "Terminate task", "Load states", "Paths"]))
async def actions_calc(message: Message):

    if message.text == "Load states":
        computer.load_from_file()

    if message.text == "Start computing":
        flag = False
        if computer.curr_stage == 0:
            computer.curr_stage = 1
            computer.start_stage(1)
            flag = True
        else:
            if not computer.stages[computer.curr_stage]:
                computer.check_curr_job_state()
                if computer.output_text != 'COMPLETED':
                    computer.start_stage(computer.curr_stage)
                    flag = True

            if computer.stages[computer.curr_stage]:
                computer.curr_stage += 1
                computer.start_stage(computer.curr_stage)
                flag = True #'''

        if (not computer.running) and flag:
            computer.running = True
            print('checking thread has been started')
            Thread(target=checking_thread).start()

    if message.text == "Curr state":
        computer.check_curr_job_state()

    if message.text == "Terminate task":
        computer.output_text = 'nothing to terminate'
        if computer.running:
            computer.check_curr_job_state()
            if computer.stages[computer.curr_stage] is False:
                computer.terminate_job() # '''
            computer.running = False

    if message.text == "Stages":
        states = ''
        for i in computer.stages:
            states = states + str(i) + ': ' + str(computer.stages[i]) + '\n'
        computer.output_text = states

    if message.text == "Paths":
        computer.output_text = computer.input_dir + '\n' + computer.output_dir

    print(message.text + ": " + computer.output_text)
    text = text_replace(computer.output_text)
    await message.answer(text=text)  # '''


def checking_thread():
    future = asyncio.run_coroutine_threadsafe(checking(), loop=loop)
    future.result()


async def checking():
    print("in checking")
    minutes = 0
    all = 0
    while computer.running:
        await asyncio.sleep(60)
        if not computer.running:
            break
        print('running')
        minutes += 1
        all += 1
        computer.check_curr_job_state()
        computer.save_to_file()
        if computer.output_text == 'FAILED':
            await bot.send_message(chat_id=admin_id, text=text_replace(f'Calculation failed. Stage: {computer.curr_stage}'))
            break
        if computer.stages[computer.curr_stage] is True:
            if computer.curr_stage == 15:
                await bot.send_message(chat_id=admin_id, text=text_replace(f'Calculation completed. \nOverall duration: {all} minutes.'))
                break
            computer.curr_stage += 1
            computer.start_stage(computer.curr_stage)
            print("checkup: " + computer.output_text)
            text = text_replace(computer.output_text + f'\nPrevious stage duration: {minutes} minutes.')
            minutes = 0
            await bot.send_message(chat_id=admin_id, text=text) # '''
    print('thread finished')
    computer.running = False



def text_replace(text):

    if len(text) == 0:
        return 'empty output'

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

