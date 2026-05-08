from __future__ import annotations


class ValidationError(ValueError):
    pass


def parse_int(text: str | None, *, field_name: str, allow_empty_to_zero: bool = True) -> int:
    raw = (text or "").strip()
    if not raw:
        if allow_empty_to_zero:
            return 0
        raise ValidationError(f"{field_name} bo'sh bo'lmasligi kerak.")

    # Users might type commands like /skip accidentally; treat as invalid for numeric fields.
    if raw.startswith("/"):
        raise ValidationError(f"{field_name} raqam bo'lishi kerak.")

    try:
        value = int(raw)
    except ValueError as e:
        raise ValidationError(f"{field_name} raqam bo'lishi kerak (masalan: 5).") from e

    if value < 0:
        raise ValidationError(f"{field_name} manfiy bo'lmasligi kerak.")

    return value


def parse_comment(text: str | None) -> str:
    raw = (text or "").strip()
    if not raw or raw.lower() == "/skip":
        return ""
    return raw


def parse_name(text: str | None) -> str:
    raw = (text or "").strip()
    return raw

