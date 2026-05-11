from __future__ import annotations

from typing import Any, Optional

import aiosqlite

from config import settings

_MANAGER_CHAT_ID_KEY = "manager_chat_id"


async def set_manager_chat_id(chat_id: int) -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            """
            INSERT INTO bot_settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value;
            """,
            (_MANAGER_CHAT_ID_KEY, str(int(chat_id))),
        )
        await db.commit()


async def get_manager_chat_id() -> Optional[int]:
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT value FROM bot_settings WHERE key = ?;",
            (_MANAGER_CHAT_ID_KEY,),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        raw = str(row["value"]).strip()
        if not raw:
            return None
        try:
            return int(raw)
        except ValueError:
            # Corrupted setting; treat as missing.
            return None


async def get_user_name(telegram_user_id: int) -> Optional[str]:
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT name FROM users WHERE telegram_user_id = ?;",
            (telegram_user_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return str(row["name"])


async def upsert_user_name(telegram_user_id: int, name: str) -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            """
            INSERT INTO users (telegram_user_id, name)
            VALUES (?, ?)
            ON CONFLICT(telegram_user_id) DO UPDATE SET name=excluded.name;
            """,
            (telegram_user_id, name),
        )
        await db.commit()


async def create_report(
    telegram_user_id: int,
    date_ddmm: str,
    *,
    name: str,
    new_leads: int,
    did_not_answer: int,
    potential: int,
    information_provided: int,
    closed: int,
    sales: int,
    comment: str,
    successful_calls: int,
    call_duration_minutes: int,
    unfinished_tasks: int,
) -> int:
    async with aiosqlite.connect(settings.db_path) as db:
        cursor = await db.execute(
            """
            INSERT INTO reports (
                telegram_user_id,
                date_ddmm,
                is_sent_to_group,
                name,
                new_leads,
                did_not_answer,
                potential,
                information_provided,
                closed,
                sales,
                comment,
                successful_calls,
                call_duration_minutes,
                unfinished_tasks
            )
            VALUES (?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                telegram_user_id,
                date_ddmm,
                name,
                new_leads,
                did_not_answer,
                potential,
                information_provided,
                closed,
                sales,
                comment,
                successful_calls,
                call_duration_minutes,
                unfinished_tasks,
            ),
        )
        await db.commit()
        return int(cursor.lastrowid)


async def update_report(
    report_id: int,
    *,
    name: str,
    new_leads: int,
    did_not_answer: int,
    potential: int,
    information_provided: int,
    closed: int,
    sales: int,
    comment: str,
    successful_calls: int,
    call_duration_minutes: int,
    unfinished_tasks: int,
) -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            """
            UPDATE reports
            SET
                name = ?,
                new_leads = ?,
                did_not_answer = ?,
                potential = ?,
                information_provided = ?,
                closed = ?,
                sales = ?,
                comment = ?,
                successful_calls = ?,
                call_duration_minutes = ?,
                unfinished_tasks = ?
            WHERE id = ?;
            """,
            (
                name,
                new_leads,
                did_not_answer,
                potential,
                information_provided,
                closed,
                sales,
                comment,
                successful_calls,
                call_duration_minutes,
                unfinished_tasks,
                report_id,
            ),
        )
        await db.commit()


async def set_report_sent(report_id: int, *, sent: bool = True) -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            "UPDATE reports SET is_sent_to_group = ? WHERE id = ?;",
            (1 if sent else 0, report_id),
        )
        await db.commit()


async def delete_report(report_id: int) -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("DELETE FROM reports WHERE id = ?;", (report_id,))
        await db.commit()


async def get_report(report_id: int) -> Optional[dict[str, Any]]:
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM reports WHERE id = ?;",
            (report_id,),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return dict(row)


async def get_last_report_for_user_date(
    telegram_user_id: int, date_ddmm: str
) -> Optional[dict[str, Any]]:
    async with aiosqlite.connect(settings.db_path) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT *
            FROM reports
            WHERE telegram_user_id = ? AND date_ddmm = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1;
            """,
            (telegram_user_id, date_ddmm),
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return dict(row)

