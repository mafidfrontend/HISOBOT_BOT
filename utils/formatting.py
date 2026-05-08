from __future__ import annotations

from datetime import datetime


def today_ddmm() -> str:
    # Local date in DD.MM format as requested.
    return datetime.now().strftime("%d.%m")


def format_report_text(*, date_ddmm: str, data: dict[str, object]) -> str:
    # Keep output formatting exactly as requested.
    name = str(data.get("name", ""))
    new_leads = int(data.get("new_leads", 0))
    did_not_answer = int(data.get("did_not_answer", 0))
    potential = int(data.get("potential", 0))
    information_provided = int(data.get("information_provided", 0))
    closed = int(data.get("closed", 0))
    sales = int(data.get("sales", 0))
    comment = str(data.get("comment", ""))
    successful_calls = int(data.get("successful_calls", 0))
    call_duration_minutes = int(data.get("call_duration_minutes", 0))
    unfinished_tasks = int(data.get("unfinished_tasks", 0))

    return (
        "#HISOBOT\n\n"
        f"ism: {name}\n"
        f"yangi lid: {new_leads}\n"
        f"Ko'tarmadi: {did_not_answer}\n"
        f"Potensial: {potential}\n"
        f"Malumot berildi: {information_provided}\n"
        f"Yopildi: {closed}\n"
        f"Sotuv: {sales}\n"
        f"Izoh: {comment}\n\n"
        f"uspeshniy zvonok: {successful_calls}\n"
        f"zvonok davomiyligi: {call_duration_minutes} minut\n"
        f"yopilmagan zadacha: {unfinished_tasks}\n\n"
        f"sana: {date_ddmm}\n"
    )

