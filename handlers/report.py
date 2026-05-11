from __future__ import annotations

import logging
from typing import Any

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import settings
from database.repository import (
    create_report,
    delete_report,
    get_last_report_for_user_date,
    get_report,
    get_user_name,
    set_report_sent,
    update_report,
    upsert_user_name,
)
from keyboards.inline import report_review_keyboard
from states.report import ReportStates
from utils.formatting import format_report_text, today_ddmm
from utils.report_fields import FIELDS
from utils.validators import ValidationError, parse_comment, parse_int, parse_name


router = Router()

logger = logging.getLogger("hisobot_bot")


def _step_count() -> int:
    return len(FIELDS)


async def _send_report_to_group(bot: Bot, report_id: int) -> bool:
    report = await get_report(report_id)
    if not report:
        return False
    if int(report.get("is_sent_to_group", 0)) == 1:
        return True

    text = format_report_text(
        date_ddmm=str(report["date_ddmm"]),
        data=report,
    )
    try:
        await bot.send_message(chat_id=settings.group_id, text=text)
        await set_report_sent(report_id, sent=True)
        return True
    except Exception:
        # Avoid crashing the bot on send failures.
        logger.exception("Failed to send report_id=%s to group", report_id)
        return False


async def _start_collecting(
    message: Message,
    state: FSMContext,
    *,
    mode: str,
    report_id: int | None = None,
    prefill: dict[str, Any] | None = None,
) -> None:
    await state.clear()

    prefill = prefill or {}
    # Default stored name for convenience.
    if not prefill.get("name"):
        prefill["name"] = await get_user_name(message.from_user.id) or message.from_user.full_name or "User"

    data = {
        "mode": mode,  # create | edit
        "report_id": report_id,
        "step": 0,
        "prefill": prefill,
        "answers": {},
        "date_ddmm": today_ddmm(),
    }
    await state.set_state(ReportStates.collecting)
    await state.update_data(**data)

    await message.answer(_field_prompt(0, prefill=prefill))


def _field_prompt(step: int, *, prefill: dict[str, Any]) -> str:
    field = FIELDS[step]
    if field.key not in prefill or prefill[field.key] in ("", None):
        return field.prompt
    # Show current value as hint.
    current = prefill[field.key]
    if field.numeric:
        return f"{field.prompt}\nHozirgi qiymat: {current}"
    if field.key == "comment":
        return f"{field.prompt}\nHozirgi izoh: {current or '-'}"
    return f"{field.prompt}\nHozirgi qiymat: {current}"


async def _finish_collecting(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    mode = str(data.get("mode", "create"))
    report_id = data.get("report_id")
    prefill: dict[str, Any] = dict(data.get("prefill") or {})
    answers: dict[str, Any] = dict(data.get("answers") or {})
    date_ddmm = str(data.get("date_ddmm") or today_ddmm())

    # Ensure name is not empty.
    name_val = str(answers.get("name", "") or "").strip()
    if not name_val:
        name_val = str(prefill.get("name") or "User")
    answers["name"] = name_val

    # Remember user's name for the next reports.
    await upsert_user_name(message.from_user.id, name_val)

    # In case user never answered all steps (shouldn't happen), enforce defaults.
    for field in FIELDS:
        if field.key not in answers:
            answers[field.key] = 0 if field.numeric else ""

    if mode == "edit" and report_id is not None:
        await update_report(
            int(report_id),
            name=str(answers["name"]),
            new_leads=int(answers["new_leads"]),
            did_not_answer=int(answers["did_not_answer"]),
            potential=int(answers["potential"]),
            information_provided=int(answers["information_provided"]),
            closed=int(answers["closed"]),
            sales=int(answers["sales"]),
            comment=str(answers["comment"]),
            successful_calls=int(answers["successful_calls"]),
            call_duration_minutes=int(answers["call_duration_minutes"]),
            unfinished_tasks=int(answers["unfinished_tasks"]),
        )
        final_report_id = int(report_id)
    else:
        final_report_id = await create_report(
            message.from_user.id,
            date_ddmm,
            name=str(answers["name"]),
            new_leads=int(answers["new_leads"]),
            did_not_answer=int(answers["did_not_answer"]),
            potential=int(answers["potential"]),
            information_provided=int(answers["information_provided"]),
            closed=int(answers["closed"]),
            sales=int(answers["sales"]),
            comment=str(answers["comment"]),
            successful_calls=int(answers["successful_calls"]),
            call_duration_minutes=int(answers["call_duration_minutes"]),
            unfinished_tasks=int(answers["unfinished_tasks"]),
        )

    # Load final report from DB and send preview.
    report = await get_report(final_report_id)
    if not report:
        await message.answer("Xatolik: hisobot saqlanmadi. Qayta urinib ko'ring.")
        return

    text = format_report_text(
        date_ddmm=str(report["date_ddmm"]),
        data=report,
    )

    kb = report_review_keyboard(final_report_id)
    await message.answer(text, reply_markup=kb)

    await state.set_state(ReportStates.review)
    await state.update_data(report_id=final_report_id)


@router.message(Command("report"))
async def report_cmd(message: Message, state: FSMContext) -> None:
    # Pre-fill stored name for convenience.
    stored_name = await get_user_name(message.from_user.id) or message.from_user.full_name or "User"
    await _start_collecting(message, state, mode="create", prefill={"name": stored_name})


@router.message(Command("today"))
async def today_cmd(message: Message, state: FSMContext) -> None:
    date_ddmm = today_ddmm()
    report = await get_last_report_for_user_date(message.from_user.id, date_ddmm)
    if not report:
        await message.answer("Bugungi hisobot topilmadi. /report orqali yangisini yarating.")
        return

    text = format_report_text(date_ddmm=str(report["date_ddmm"]), data=report)
    kb = report_review_keyboard(int(report["id"]))
    await message.answer(text, reply_markup=kb)

    await state.set_state(ReportStates.review)
    await state.update_data(report_id=int(report["id"]))


@router.message(Command("edit"))
async def edit_cmd(message: Message, state: FSMContext) -> None:
    date_ddmm = today_ddmm()
    report = await get_last_report_for_user_date(message.from_user.id, date_ddmm)
    if not report:
        await message.answer("Bugungi hisobot topilmadi. /report orqali yangisini yarating.")
        return
    if int(report.get("is_sent_to_group", 0)) == 1:
        await message.answer("Yuborilgan hisobotni tahrirlab bo'lmaydi. 'Regenerate' ni ishlating.")
        return

    prefill = dict(report)
    prefill["name"] = str(report.get("name") or "")
    await _start_collecting(
        message,
        state,
        mode="edit",
        report_id=int(report["id"]),
        prefill=prefill,
    )


@router.message(Command("send"))
async def send_cmd(message: Message, state: FSMContext, bot: Bot) -> None:
    date_ddmm = today_ddmm()
    report = await get_last_report_for_user_date(message.from_user.id, date_ddmm)
    if not report:
        await message.answer("Bugungi hisobot topilmadi. /report orqali yangisini yarating.")
        return

    if int(report.get("is_sent_to_group", 0)) == 1:
        await message.answer("Bu hisobot allaqachon guruhga yuborilgan.")
        return

    ok = await _send_report_to_group(bot, int(report["id"]))
    if ok:
        await message.answer("Guruhga yuborildi.")
    else:
        await message.answer("Yuborishda xatolik bo'ldi. Qayta urinib ko'ring.")

    await state.set_state(ReportStates.review)
    await state.update_data(report_id=int(report["id"]))


@router.message(Command("cancel"), ReportStates.collecting)
async def cancel_collecting_cmd(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Bekor qilindi.")


@router.message(Command("cancel"), ReportStates.review)
async def cancel_review_cmd(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    report_id = data.get("report_id")
    if report_id is not None:
        report = await get_report(int(report_id))
        if report and int(report.get("is_sent_to_group", 0)) == 0:
            await delete_report(int(report_id))
    await state.clear()
    await message.answer("Bekor qilindi.")


@router.message(Command("cancel"))
async def cancel_fallback_cmd(message: Message) -> None:
    await message.answer("Hech narsa bekor qilinmadi.")


@router.message(ReportStates.collecting)
async def collecting_handler(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    step = int(data.get("step", 0))
    prefill: dict[str, Any] = dict(data.get("prefill") or {})
    answers: dict[str, Any] = dict(data.get("answers") or {})

    if step >= _step_count():
        await message.answer("Jarayon tugagan. Inline tugmalarni bosing.")
        return

    field = FIELDS[step]
    try:
        if field.key == "name":
            # Allow empty -> will be replaced with stored name on finish.
            answers["name"] = parse_name(message.text)
        elif field.key == "comment":
            raw = (message.text or "").strip()
            if raw.lower() == "/skip":
                # Keep previously stored comment when skipping during edit.
                answers["comment"] = str(prefill.get("comment") or "")
            else:
                answers["comment"] = parse_comment(message.text)
        elif field.numeric:
            answers[field.key] = parse_int(
                message.text,
                field_name=field.output_label,
                allow_empty_to_zero=True,
            )
        else:
            answers[field.key] = message.text or ""
    except ValidationError as e:
        await message.answer(f"Xato: {e}")
        # Re-ask same field.
        await message.answer(_field_prompt(step, prefill=prefill))
        return

    step += 1
    if step < _step_count():
        await state.update_data(step=step, answers=answers)
        await message.answer(_field_prompt(step, prefill=prefill))
        return

    await state.update_data(step=step, answers=answers)
    await _finish_collecting(message, state)

