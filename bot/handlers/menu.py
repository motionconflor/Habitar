"""Обработчик меню и данных из WebApp."""

import json
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext

from config import ABOUT_TEXT, HELP_TEXT
from db import get_or_create_user, unlock_user, complete_lesson_db, get_lessons_for_course, get_user_progress
from states import ProgramState

router = Router()

WEBAPP_URL = "https://vlady6113-blip.github.io/motion-habitar/webapp/"
MERCADOPAGO_LINK = "https://mpago.la/2Ghk3Vm"
WHATSAPP_LINK = "https://wa.me/5491132787456?text=Hola%21+Quisiera+info+sobre+el+programa+HABITAR"


def webapp_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🕊️ Abrir HABITAR", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton(text="💳 Comprar con MercadoPago", url=MERCADOPAGO_LINK)],
        [InlineKeyboardButton(text="💬 Consultar por WhatsApp", url=WHATSAPP_LINK)],
        [InlineKeyboardButton(text="ℹ️ Sobre MOTioN", callback_data="about")],
        [InlineKeyboardButton(text="📊 Mi progreso", callback_data="progress")],
    ])


@router.message(Command("menu"))
@router.message(F.text.lower().in_({"menu", "menú", "menú"}))
async def cmd_menu(message: Message, state: FSMContext):
    await state.set_state(ProgramState.menu)
    user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    status = "✅ Acceso activo" if user["unlocked"] else "🔒 Sin acceso"
    await message.answer(
        f"🕊️ *MOTioN — HABITAR*\n\n"
        f"Tu estado: {status}\n\n"
        f"Abrí la aplicación para continuar:",
        parse_mode="Markdown",
        reply_markup=webapp_kb(),
    )


@router.message(F.web_app_data)
async def webapp_data(message: Message, state: FSMContext):
    """Обрабатывает данные из Mini App."""
    user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    try:
        data = json.loads(message.web_app_data.data)
    except (json.JSONDecodeError, TypeError):
        await message.answer("❌ Error al recibir datos.")
        return

    action = data.get("action", "")
    lesson_id = data.get("lesson_id")
    reflection = data.get("reflection", "")

    if action == "complete_lesson" and lesson_id:
        complete_lesson_db(message.from_user.id, lesson_id, reflection)

        all_lessons = get_lessons_for_course('habitar')
        completed = get_user_progress(message.from_user.id, 'habitar')
        total = len(all_lessons)

        if len(completed) >= total:
            await message.answer(
                "🕊️ *¡HABITAR completado!*\n\n"
                "Los cuatro estados viven en vos ahora.\n"
                "PAUSAR, LIBERAR, FLUIR, HABITAR.\n\n"
                "Gracias por recorrer este camino.",
                parse_mode="Markdown",
            )
        else:
            next_order = len(completed) + 1
            next_title = ""
            for ls in all_lessons:
                if ls["lesson_order"] == next_order:
                    next_title = ls["title"]
                    break

            await message.answer(
                f"✅ *{data.get('title', 'Lección')} — completado.*\n\n"
                f"Progreso: {len(completed)}/{total}\n"
                f"Próximo estado: *{next_title or '—'}*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🕊️ Continuar en HABITAR", web_app=WebAppInfo(url=WEBAPP_URL))],
                ]),
            )

    elif action == "get_progress":
        completed = get_user_progress(message.from_user.id, 'habitar')
        all_lessons = get_lessons_for_course('habitar')
        await message.answer(
            f"📊 Progreso: {len(completed)}/{len(all_lessons)}",
        )

    elif action == "unlock_request":
        await message.answer(
            "💳 Para activar tu acceso, realizá el pago:\n"
            f"[Comprar con MercadoPago]({MERCADOPAGO_LINK})\n\n"
            "Una vez abonado, usá /unlock <código> o contactanos por WhatsApp.",
            parse_mode="Markdown",
        )


@router.callback_query(F.data == "about")
async def cb_about(callback: CallbackQuery):
    await callback.message.edit_text(ABOUT_TEXT, reply_markup=webapp_kb())
    await callback.answer()


@router.callback_query(F.data == "support")
async def cb_support(callback: CallbackQuery):
    await callback.message.edit_text(HELP_TEXT, reply_markup=webapp_kb())
    await callback.answer()


@router.callback_query(F.data == "progress")
async def cb_progress(callback: CallbackQuery):
    user_id = callback.from_user.id
    get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)
    completed = get_user_progress(user_id, 'habitar')
    all_lessons = get_lessons_for_course('habitar')
    total = len(all_lessons)
    done = len(completed)

    bar_width = 10
    filled = int(bar_width * done / total) if total > 0 else 0
    bar = "▓" * filled + "░" * (bar_width - filled)

    await callback.message.edit_text(
        f"📊 *Tu progreso en HABITAR*\n\n"
        f"[{bar}] {done}/{total} completados\n\n"
        f"{'🕊️ ¡Completaste todos los estados!' if done >= total else 'Seguí avanzando en el WebApp.'}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🕊️ Abrir HABITAR", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton(text="⬅️ Volver al menú", callback_data="menu_back")],
        ]),
    )
    await callback.answer()


@router.callback_query(F.data == "menu_back")
async def cb_menu_back(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProgramState.menu)
    user = get_or_create_user(callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    status = "✅ Acceso activo" if user["unlocked"] else "🔒 Sin acceso"
    await callback.message.edit_text(
        f"🕊️ *MOTioN — HABITAR*\n\nTu estado: {status}",
        parse_mode="Markdown",
        reply_markup=webapp_kb(),
    )
    await callback.answer()


@router.message(Command("unlock"))
async def cmd_unlock(message: Message, state: FSMContext):
    user = get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    unlock_user(message.from_user.id)
    await message.answer(
        "✅ *Acceso activado.*\n\n"
        "Bienvenida a HABITAR. Abrí la app para comenzar tu recorrido.",
        parse_mode="Markdown",
        reply_markup=webapp_kb(),
    )
    await state.set_state(ProgramState.menu)
