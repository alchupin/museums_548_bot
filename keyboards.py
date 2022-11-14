from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b_start = KeyboardButton('О боте')
b_help = KeyboardButton('Инструкция')

kb = ReplyKeyboardMarkup(resize_keyboard=True)

kb.row(b_start, b_help)