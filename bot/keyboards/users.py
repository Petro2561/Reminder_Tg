from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_kb(width: int, *args: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text=button, callback_data=f"set_timezone:{button}")
        for button in args
    ]
    kb_builder.row(*buttons, width=width)
    return kb_builder.as_markup()


def get_timezone_keyboard() -> InlineKeyboardMarkup:
    timezones = [
        "UTC-12",
        "UTC-11",
        "UTC-10",
        "UTC-9",
        "UTC-8",
        "UTC-7",
        "UTC-6",
        "UTC-5",
        "UTC-4",
        "UTC-3",
        "UTC-2",
        "UTC-1",
        "UTC+0",
        "UTC+1",
        "UTC+2",
        "UTC+3",
        "UTC+4",
        "UTC+5",
        "UTC+6",
        "UTC+7",
        "UTC+8",
        "UTC+9",
        "UTC+10",
        "UTC+11",
        "UTC+12",
    ]
    return create_inline_kb(3, *timezones)
