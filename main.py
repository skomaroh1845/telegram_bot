import asyncio
from threading import Thread

from aiogram import Bot, Dispatcher, executor
from config import BOT_TOKEN
from computing import Computer


loop = asyncio.get_event_loop()
bot = Bot(BOT_TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher(bot, loop=loop)
computer = Computer()

if __name__ == "__main__":
    from handlers import dp, send_to_admin, shutdowning
    executor.start_polling(dp,
                           on_startup=send_to_admin,
                           on_shutdown=shutdowning)

