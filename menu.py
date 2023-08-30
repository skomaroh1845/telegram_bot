from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Start computing")
        ],
        [
            KeyboardButton(text="Current state")
        ],
        [
            KeyboardButton(text="Terminate task")
        ]
    ],
    resize_keyboard=True
)

common_commands = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="ls"),
            KeyboardButton(text="squeue")
        ],
        [
            KeyboardButton(text="sinfo")
        ]
    ],
    resize_keyboard=True
)