"""Обработчик /start — открытие WebApp с контекстом курса."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext

from config import WELCOME_TEXT
from db import get_or_create_user, get_course

router = Router()

WEBAPP_BASE = "https://vlady6113-blip.github.io/motion-habitar/webapp/"


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
    )

    course = get_course('habitar')
    price = f"${course['price_promo']:,}".replace(',', '.') if course else "$29.000"

    await message.answer(
        WELCOME_TEXT,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🕊️ Abrir HABITAR",
                web_app=WebAppInfo(url=WEBAPP_BASE),
            )],
            [InlineKeyboardButton(
                text=f"💳 Comprar ({price} ARS)",
                url="https://mpago.la/2Ghk3Vm",
            )],
            [InlineKeyboardButton(
                text="💬 Consultar por WhatsApp",
                url="https://wa.me/5491132787456?text=Hola%21+Quisiera+info+sobre+el+programa+HABITAR",
            )],
            [InlineKeyboardButton(
                text="ℹ️ Sobre el programa",
                callback_data="about",
            )],
        ]),
    )
