from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database.repository import upsert_user_name


router = Router()


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
        "Salom!\n"
        "Kunlik hisobotni tez yaratish uchun:\n"
        "/report\n\n"
        "Bugungi hisobotni ko'rish uchun:\n"
        "/today\n"
    )

