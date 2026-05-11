import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from database.repository import set_manager_chat_id, upsert_user_name


router = Router()
logger = logging.getLogger("hisobot_bot")


@router.message(CommandStart())
async def start_cmd(message: Message) -> None:
    if message.from_user:
        suggested_name = (
            message.from_user.full_name
            or message.from_user.username
            or message.from_user.first_name
            or "User"
        )
        await upsert_user_name(message.from_user.id, suggested_name.strip())

    await message.answer(
        f"Debug chat id: {message.chat.id}\n\n"
        "Salom!\n"
        "Kunlik hisobotni tez yaratish uchun:\n"
        "/report\n\n"
        "Bugungi hisobotni ko'rish uchun:\n"
        "/today\n"
    )


@router.message(Command("setmanager"))
async def setmanager_cmd(message: Message) -> None:
    try:
        await set_manager_chat_id(int(message.chat.id))
    except Exception:
        logger.exception("Failed to set manager chat id. chat_id=%s", message.chat.id)
        await message.answer("Xatolik: menejerni sozlab bo'lmadi. Keyinroq urinib ko'ring.")
        return

    await message.answer("✅ You have been set as the manager")

