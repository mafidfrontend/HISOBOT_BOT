import aiosqlite

from config import settings


async def init_db() -> None:
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL,
                date_ddmm TEXT NOT NULL,
                is_sent_to_group INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),

                name TEXT NOT NULL,
                new_leads INTEGER NOT NULL,
                did_not_answer INTEGER NOT NULL,
                potential INTEGER NOT NULL,
                information_provided INTEGER NOT NULL,
                closed INTEGER NOT NULL,
                sales INTEGER NOT NULL,
                comment TEXT NOT NULL,
                successful_calls INTEGER NOT NULL,
                call_duration_minutes INTEGER NOT NULL,
                unfinished_tasks INTEGER NOT NULL
            );
            """
        )
        await db.commit()

