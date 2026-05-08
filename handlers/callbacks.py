from __future__ import annotations

from typing import Any

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.repository import delete_report, get_report
from handlers.report import _start_collecting
from handlers.report import _send_report_to_group


router = Router()


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
        ok = await _send_report_to_group(bot, report_id)
        if ok:
            await callback.answer("Guruhga yuborildi.")
        else:
            await callback.answer("Yuborishda xatolik bo'ldi. Qayta urinib ko'ring.", show_alert=True)
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

