from __future__ import annotations

import re
import unicodedata
from typing import Any

_NON_WORD_RE = re.compile(r"[^\w\s]+", re.UNICODE)
_SPACE_RE = re.compile(r"\s+")


def normalise_search_query(value: str) -> str:
    """Return the canonical form used for local place search."""
    text = unicodedata.normalize("NFKC", value).casefold().strip()
    text = _NON_WORD_RE.sub(" ", text)
    return _SPACE_RE.sub(" ", text).strip()


def stable_source_key(source: str, object_type: str, object_id: Any) -> str:
    return f"{source.casefold()}:{str(object_type).casefold()}:{object_id}"


def formatted_place_name(
    name: str,
    *,
    street: str | None = None,
    city: str | None = None,
    district: str | None = None,
    region: str | None = None,
    country: str | None = "Pakistan",
) -> str:
    parts = [name, street, city, district, region, country]
    seen: set[str] = set()
    output: list[str] = []
    for part in parts:
        if not part:
            continue
        key = normalise_search_query(part)
        if key and key not in seen:
            seen.add(key)
            output.append(part)
    return ", ".join(output)
