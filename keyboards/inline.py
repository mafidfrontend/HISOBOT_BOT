from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def report_review_keyboard(report_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Send to group",
                    callback_data=f"report:send:{report_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Edit",
                    callback_data=f"report:edit:{report_id}",
                ),
                InlineKeyboardButton(
                    text="Regenerate",
                    callback_data=f"report:regen:{report_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Cancel",
                    callback_data=f"report:cancel:{report_id}",
                )
            ],
        ]
    )

