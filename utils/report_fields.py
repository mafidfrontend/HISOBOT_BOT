from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldDef:
    key: str
    prompt: str
    output_label: str
    numeric: bool = False
    optional: bool = False


FIELDS: list[FieldDef] = [
    FieldDef(key="name", prompt="ismingizni kiriting (raqam emas). Bo'sh qoldirsangiz saqlangan ismdan foydalaniladi:", output_label="ism", numeric=False),
    FieldDef(key="new_leads", prompt="yangi lid (raqam):", output_label="yangi lid", numeric=True),
    FieldDef(key="did_not_answer", prompt="Ko'tarmadi (raqam):", output_label="Ko'tarmadi", numeric=True),
    FieldDef(key="potential", prompt="Potensial (raqam):", output_label="Potensial", numeric=True),
    FieldDef(key="information_provided", prompt="Malumot berildi (raqam):", output_label="Malumot berildi", numeric=True),
    FieldDef(key="closed", prompt="Yopildi (raqam):", output_label="Yopildi", numeric=True),
    FieldDef(key="sales", prompt="Sotuv (raqam):", output_label="Sotuv", numeric=True),
    FieldDef(key="comment", prompt="Izoh (ixtiyoriy). Yozishni istamasangiz /skip:", output_label="Izoh", numeric=False, optional=True),
    FieldDef(key="successful_calls", prompt="uspeshniy zvonok (raqam):", output_label="uspeshniy zvonok", numeric=True),
    FieldDef(key="call_duration_minutes", prompt="zvonok davomiyligi (minut, raqam):", output_label="zvonok davomiyligi", numeric=True),
    FieldDef(key="unfinished_tasks", prompt="yopilmagan zadacha (raqam):", output_label="yopilmagan zadacha", numeric=True),
]

