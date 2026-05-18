"""Обработчики уроков — запуск, прохождение, рефлексия."""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards.inline import lesson_complete_keyboard, reflection_keyboard, lesson_start_keyboard
from keyboards.main_menu import main_menu_keyboard
from services.lesson_service import get_lesson, get_total_lessons
from services.user_service import get_user, complete_lesson
from states import ProgramState

router = Router()


@router.callback_query(F.data.startswith("lesson_start:"))
async def cb_lesson_start(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split(":")[1])
    user = get_user(callback.from_user.id)

    if not user["unlocked"]:
        await callback.answer("Primero necesitás desbloquear el acceso con /unlock", show_alert=True)
        return

    lesson = get_lesson(lesson_id)
    if not lesson:
        await callback.answer("Lección no encontrada", show_alert=True)
        return

    await callback.message.edit_reply_markup(reply_markup=None)

    # Отправляем видео
    await callback.message.answer(
        f"🎬 *{lesson['title']}*\n"
        f"⏱ {lesson['duration']}\n\n"
        f"[Ver video]({lesson['video_url']})",
        parse_mode="Markdown",
        disable_web_page_preview=False,
    )

    # Затем вопросы рефлексии
    await callback.message.answer(
        f"🌿 *Reflexión*\n\n"
        f"{lesson['reflection']}",
        parse_mode="Markdown",
        reply_markup=reflection_keyboard(lesson_id),
    )
    await state.set_state(ProgramState.reflection)
    await callback.answer()


@router.callback_query(F.data.startswith("complete:"))
async def cb_complete(callback: CallbackQuery, state: FSMContext):
    lesson_id = int(callback.data.split(":")[1])
    user = complete_lesson(callback.from_user.id, lesson_id)
    lesson = get_lesson(lesson_id)

    await callback.message.edit_reply_markup(reply_markup=None)

    # Сообщение о завершении
    await callback.message.answer(
        f"✅ *{lesson['title']} — completado*\n\n"
        f"{lesson['completion']}",
        parse_mode="Markdown",
    )

    # Показываем меню — todas las experiencias están desbloqueadas desde el inicio
    if lesson_id < get_total_lessons():
        next_lesson = get_lesson(lesson_id + 1)
        await callback.message.answer(
            f"✨ Todas las experiencias están disponibles. Cuando quieras, continuá con *{next_lesson['title']}*:",
            parse_mode="Markdown",
            reply_markup=lesson_start_keyboard(lesson_id + 1),
        )
    else:
        await callback.message.answer(
            "🕊️ *HABITAR completado.*\n\n"
            "Los cuatro estados viven en vos ahora.\n"
            "Gracias por recorrer este camino.\n\n"
            "Siempre podés volver.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )

    await state.set_state(ProgramState.menu)
    await callback.answer("✅ Completado")
