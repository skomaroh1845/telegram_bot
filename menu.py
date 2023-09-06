from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Start computing")
        ],
        [
            KeyboardButton(text="Curr state"),
            KeyboardButton(text="Stages")
        ],
        [
            KeyboardButton(text="Load states"),
            KeyboardButton(text="Paths")
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
            KeyboardButton(text="sinfo"),
            KeyboardButton(text="last file")
        ]
    ],
    resize_keyboard=True
)