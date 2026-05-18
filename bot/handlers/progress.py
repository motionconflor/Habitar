"""Обработчик прогресса."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.user_service import get_user
from services.lesson_service import get_total_lessons, get_lesson_title

router = Router()


@router.message(F.text == "📊 Progreso")
async def progreso_button(message: Message, state: FSMContext):
    user = get_user(message.from_user.id)
    total = get_total_lessons()
    completed = len(user["completed"])
    current = user["current_lesson"] or 1

    bar_width = 10
    filled = int(bar_width * completed / total) if total > 0 else 0
    bar = "▓" * filled + "░" * (bar_width - filled)

    if completed == total:
        await message.answer(
            f"📊 *Progreso*\n\n"
            f"[{bar}] {completed}/{total} completados\n\n"
            f"🕊️ *¡Completaste el recorrido!*",
            parse_mode="Markdown",
        )
    else:
        next_title = get_lesson_title(current)
        await message.answer(
            f"📊 *Progreso*\n\n"
            f"[{bar}] {completed}/{total} completados\n\n"
            f"Próximo estado: *{next_title}*",
            parse_mode="Markdown",
        )
