from __future__ import annotations

import logging
from typing import Any

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.repository import delete_report, get_manager_chat_id, get_report
from handlers.report import _start_collecting
from handlers.report import _send_report_to_group
from utils.formatting import format_report_text


router = Router()
logger = logging.getLogger("hisobot_bot")


@router.callback_query(F.data.startswith("report:"))
async def report_callback_handler(
    callback: CallbackQuery, state: FSMContext, bot: Bot
) -> None:
    try:
        _, action, report_id_str = callback.data.split(":", 2)
        report_id = int(report_id_str)
    except Exception:
        await callback.answer("Noto'g'ri tugma.", show_alert=True)
        return

    report = await get_report(report_id)
    if not report:
        await callback.answer("Hisobot topilmadi.", show_alert=True)
        return

    if int(report.get("telegram_user_id", -1)) != callback.from_user.id:
        await callback.answer("Bu tugma sizniki emas.", show_alert=True)
        return

    is_sent = int(report.get("is_sent_to_group", 0)) == 1

    if action == "cancel":
        if not is_sent:
            await delete_report(report_id)
        await state.clear()
        await callback.answer("Bekor qilindi.")
        return

    if action == "send":
        if is_sent:
            await callback.answer("Ushbu hisobot allaqachon guruhga yuborilgan.", show_alert=True)
            return

        report_text = format_report_text(
            date_ddmm=str(report["date_ddmm"]),
            data=report,
        )

        ok = await _send_report_to_group(bot, report_id)
        if not ok:
            await callback.answer("Yuborishda xatolik bo'ldi. Qayta urinib ko'ring.", show_alert=True)
            return

        try:
            manager_chat_id = await get_manager_chat_id()
        except Exception:
            logger.exception("Failed to load manager chat id from DB. report_id=%s", report_id)
            await callback.answer(
                "Xatolik: menejer chat ID ni o'qib bo'lmadi. Admin bazani tekshirsin.",
                show_alert=True,
            )
            return

        if manager_chat_id is None:
            logger.error("Manager chat id is missing; cannot send report_id=%s to manager", report_id)
            await callback.answer(
                "Xatolik: menejer belgilanmagan. Menejer /setmanager buyrug'ini ishlatsin.",
                show_alert=True,
            )
            return

        try:
            await bot.send_message(chat_id=manager_chat_id, text=report_text)
        except TelegramForbiddenError:
            # Typically happens when manager never pressed /start or blocked the bot.
            logger.warning(
                "Manager chat is not reachable (no /start or blocked). manager_chat_id=%s report_id=%s",
                manager_chat_id,
                report_id,
            )
            await callback.answer(
                "Xatolik: menejer botni ishga tushirmagan (/start) yoki bot bloklangan.",
                show_alert=True,
            )
            return
        except TelegramBadRequest:
            logger.exception(
                "BadRequest when sending report_id=%s to manager_chat_id=%s",
                report_id,
                manager_chat_id,
            )
            await callback.answer("Xatolik: menejer chat_id noto'g'ri yoki chat topilmadi.", show_alert=True)
            return
        except Exception:
            logger.exception(
                "Unexpected error sending report_id=%s to manager_chat_id=%s",
                report_id,
                manager_chat_id,
            )
            await callback.answer("Xatolik: menejerga yuborib bo'lmadi. Qayta urinib ko'ring.", show_alert=True)
            return

        await callback.answer("✅ Report has been sent to the manager")
        return

    if action == "edit":
        if is_sent:
            await callback.answer("Yuborilgan hisobot tahrirlanmaydi. Regenerate ni ishlating.", show_alert=True)
            return
        prefill: dict[str, Any] = dict(report)
        await _start_collecting(
            callback.message,
            state,
            mode="edit",
            report_id=report_id,
            prefill=prefill,
        )
        await callback.answer()
        return

    if action == "regen":
        # Re-generate creates a new report; optionally delete old draft if it was not sent.
        prefill = dict(report)
        await _start_collecting(
            callback.message,
            state,
            mode="create",
            report_id=None,
            prefill=prefill,
        )
        await callback.answer()
        return

    await callback.answer("Noma'lum amal.", show_alert=True)

