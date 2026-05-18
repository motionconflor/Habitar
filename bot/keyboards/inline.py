"""Инлайн-клавиатуры для уроков и действий."""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.lesson_service import get_lesson, get_total_lessons


def lesson_start_keyboard(lesson_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="▶️ Iniciar clase",
            callback_data=f"lesson_start:{lesson_id}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Volver al menú",
            callback_data="menu"
        )],
    ])


def lesson_complete_keyboard(lesson_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text="✅ Marcar como completado",
            callback_data=f"complete:{lesson_id}"
        )],
    ]
    # Если есть следующий урок, добавляем кнопку
    if lesson_id < get_total_lessons():
        next_lesson = get_lesson(lesson_id + 1)
        if next_lesson:
            buttons.insert(0, [InlineKeyboardButton(
                text=f"Siguiente: {next_lesson['title']} →",
                callback_data=f"lesson_start:{lesson_id + 1}"
            )])
    buttons.append([InlineKeyboardButton(
        text="⬅️ Volver al menú",
        callback_data="menu"
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def reflection_keyboard(lesson_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Completar",
            callback_data=f"complete:{lesson_id}"
        )],
        [InlineKeyboardButton(
            text="⬅️ Volver al menú",
            callback_data="menu"
        )],
    ])
