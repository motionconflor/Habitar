"""Клавиатура главного меню."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="▶️ Comenzar programa")],
            [KeyboardButton(text="📍 Continuar")],
            [KeyboardButton(text="📊 Progreso")],
            [KeyboardButton(text="ℹ️ Sobre MOTioN")],
            [KeyboardButton(text="💬 Soporte")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Elegí una opción...",
    )
