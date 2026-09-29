from __future__ import annotations

import json
from pathlib import Path
from .models import Listing


def read_input_ads(path: str = "data/input_ads.json", limit: int = 30) -> list[Listing]:
    file = Path(path)
    if not file.exists():
        return []
    raw = json.loads(file.read_text(encoding="utf-8"))
    listings = []
    for item in raw[:limit]:
        listings.append(Listing(
            title=str(item.get("title", "")),
            url=str(item.get("url", "")),
            price_eur=float(item["price_eur"]) if item.get("price_eur") is not None else None,
            location=str(item.get("location", "")),
            latitude=item.get("latitude"),
            longitude=item.get("longitude"),
            description=str(item.get("description", "")),
            published_at=str(item.get("published_at", "")),
            image_urls=item.get("image_urls") or [],
            source_search=str(item.get("source_search", "")),
        ))
    return listings
