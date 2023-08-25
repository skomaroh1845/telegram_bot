from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Connect to cluster")
        ],
        [
            KeyboardButton(text="Kill a bot")
        ]
    ],
    resize_keyboard=True
)