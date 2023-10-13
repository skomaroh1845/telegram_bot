import asyncio

from main import bot, dp, computer, loop
import os

from threading import Thread
from time import sleep

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Command, Text
from config import admin_id, user, path_to_input, path_to_output, NUM_OF_INSTANCE

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
    await message.answer(text=text_replace('commands:'))
    await message.answer(text=text_replace('$[command_slurm]'))
    await message.answer(text=text_replace('add_rsite='))
    await message.answer(text=text_replace('reset='))
    await message.answer(text=text_replace('input='))
    await message.answer(text=text_replace('output='))
    await message.answer(text=text_replace('stage='))
    await message.answer(text=text_replace('set_dir_list\ndir1\ndir2\n...'))
    await message.answer(text=text_replace('/menu'))
    await message.answer(text=text_replace('/common'))


@dp.message_handler(Text(startswith='set_dir_list'))
async def set_dir_list(message: Message):
    dirs = message.text.split('\n')
    if len(dirs) < 2:
        await message.answer(text=text_replace('usage:\nset_dir_list\ndir1\ndir2\n...\nwhere dir_i - name of input subfolder'))
    else:
        computer.set_dir_lists(dirs[1:])
        await message.answer(text=text_replace('dirs list written'))


@dp.message_handler(Text(startswith='$'))
async def terminal(message: Message):
    print('Command: ' + message.text[1:] + '\n')
    try:
        os.system(f'ssh {user} "' + message.text[1:] + f'" > output{NUM_OF_INSTANCE}.txt')
        try:
            with open(f'output{NUM_OF_INSTANCE}.txt', 'r') as f:
                text = f.read()
        except:
            text = 'output file cannot be read'
    except:
        text = f'command {message.text[1:]} was not executed'

    text = text_replace(text)
    await message.answer(text=text)

@dp.message_handler(Text(startswith="add_rsite="))
async def set_rsite(message: Message):
    site = ''
    try:
        site = message.text[10:]
    except:
        pass
    if site != '':
        computer.add_r_site(message.text[10:])
        computer.save_to_file()
        await message.answer(text=text_replace(f'added restrict site: {message.text[10:]}'))
    else:
        await message.answer(text=text_replace('usage:\n' + 'add_rsite=NN/NN'))

@dp.message_handler(Text(startswith="reset="))
async def reset_parameters(message: Message):
    param = ''
    try:
        param = message.text[6:]
    except:
        pass
    if param == 'input':
        computer.input_dir = path_to_input
    elif param == 'output':
        computer.output_dir = path_to_output
    elif param == 'rsites':
        computer.r_site = ''
    else:
        await message.answer(text=text_replace(f'parameters:\ninput\noutput\nstage\nrsites'))
        return
    await message.answer(text=text_replace(f'parameter {param} reset to default'))


@dp.message_handler(Text(startswith="input="))
async def set_input(message: Message):
    computer.input_dir = message.text[6:]
    computer.save_to_file()
    await message.answer(text=text_replace(f'input dir changed to: {computer.input_dir}'))


@dp.message_handler(Text(startswith="output="))
async def set_output(message: Message):
    computer.output_dir = message.text[7:]
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
        os.system(f'ssh {user} "' + command + f'" > output{NUM_OF_INSTANCE}.txt')
        try:
            with open(f'output{NUM_OF_INSTANCE}.txt', 'r') as f:
                text = f.read()
        except:
            text = 'output file cannot be read'
    except:
        text = f'command "{command}" was not executed'

    text = text_replace(text) 

    await message.answer(text=text)


@dp.message_handler(Text(startswith="sample="))
async def set_sample(message: Message):
    computer.curr_sample = int(message.text[7:])
    computer.job_num = ''
    print(f'curr sample changed to {computer.curr_sample}')
    computer.save_to_file()
    await message.answer(text=text_replace(f'curr sample changed to {computer.curr_sample}'))


@dp.message_handler(Text(startswith="stage="))
async def set_stage(message: Message):
    computer.curr_stage = int(message.text[6:])
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
                await bot.send_message(chat_id=admin_id, text=text_replace(f'Calculation completed. Sample {computer.sample_names[computer.curr_sample]} \nOverall duration: {all} minutes.'))
                if len(computer.sample_names) - computer.curr_sample > 1:
                    computer.curr_sample += 1
                    all = 0
                    computer.curr_stage = 1
                    for i in computer.stages:
                        if i < computer.curr_stage:
                            computer.stages[i] = True
                        else:
                            computer.stages[i] = False
                    computer.job_num = ''
                    computer.save_to_file()
                    minutes = 0
                else:
                    break
            else:
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

