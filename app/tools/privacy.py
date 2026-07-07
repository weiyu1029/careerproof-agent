from __future__ import annotations

import re


def redact_personal_info(text: str) -> str:
    """Redact personal identifiers before using candidate context."""
    text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", "[REDACTED_EMAIL]", text)
    text = re.sub(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]", text)
    text = re.sub(r"https?://(?:www\.)?linkedin\.com/[^\s]+", "[REDACTED_LINKEDIN]", text)
    return text
