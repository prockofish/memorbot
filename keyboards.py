from aiogram.types import InlineKeyboardMarkup as InMarkup, InlineKeyboardButton as InButton
from aiogram.types import ReplyKeyboardMarkup as ReMarkup, KeyboardButton as ReButton

class inline:
    agree = InMarkup( inline_keyboard=[
        [InButton( text="Я согласен", callback_data="agree" )]
    ], resize_keyboard=True )

    gender = InMarkup( inline_keyboard=[
        [InButton( text="М", callback_data="M" ),
        InButton( text="Ж", callback_data="W" )]
    ], resize_keyboard=True )

    params = InMarkup( inline_keyboard=[
        [InButton( text="Случайность", callback_data="random" )],
        [InButton( text="Забываемость", callback_data="memoriz" )],
        [InButton( text="По времени", callback_data="time" )],
        [InButton( text="Забыв. и врем.", callback_data="mem-time" )]
    ], resize_keyboard=True )

    help_button = InMarkup( inline_keyboard=[
        [InButton( text="Помощь", callback_data="help" )]
    ], resize_keyboard=True )

class reply:
    main = ReMarkup( keyboard=[
        [ReButton( text="Начать обучение" )],
        [ReButton( text="Выбрать словарь" )],
        [ReButton( text="Добавить словарь" )],
        [ReButton( text="Настройки" )],
        [ReButton( text="Помощь" )]
    ], resize_keyboard=True )