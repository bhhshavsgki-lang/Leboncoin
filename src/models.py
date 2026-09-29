from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import re
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_url(url: str) -> str:
    return re.sub(r"[?#].*$", "", (url or "").strip()).rstrip("/")


def stable_id(url: str, title: str = "") -> str:
    value = normalize_url(url) or f"{title.strip().lower()}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


@dataclass
class Listing:
    title: str
    url: str
    price_eur: float | None = None
    location: str = ""
    latitude: float | None = None
    longitude: float | None = None
    description: str = ""
    published_at: str = ""
    image_urls: list[str] | None = None
    source_email_date: str = ""
    source_search: str = ""

    @property
    def id(self) -> str:
        return stable_id(self.url, self.title)

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["id"] = self.id
        return data
