"""Sanitize user-controlled text before inclusion in LLM prompts."""

import re

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_llm_text(value: str | None, *, max_length: int = 120) -> str:
    if not value:
        return ""
    cleaned = _CONTROL_CHARS.sub("", value).strip()
    if len(cleaned) > max_length:
        return cleaned[:max_length]
    return cleaned


def sanitize_llm_record(record: dict, text_fields: tuple[str, ...]) -> dict:
    out = dict(record)
    for field in text_fields:
        if field in out and isinstance(out[field], str):
            out[field] = sanitize_llm_text(out[field])
    return out
