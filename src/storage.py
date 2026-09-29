from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Any


class StateStore:
    def __init__(self, path: str = "data/state.json", keep_days: int = 90):
        self.path = Path(path)
        self.keep_days = keep_days
        self.data: dict[str, Any] = {"seen": {}, "price_history": {}, "decisions": {}, "drafts": [], "runs": []}
        if self.path.exists():
            self.data.update(json.loads(self.path.read_text(encoding="utf-8")))

    def seen(self, listing_id: str) -> bool:
        return listing_id in self.data["seen"]

    def mark_seen(self, listing: dict[str, Any], decision: dict[str, Any]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.data["seen"][listing["id"]] = {"first_seen": now, "listing": listing}
        self.data["decisions"][listing["id"]] = {"at": now, "decision": decision}
        if listing.get("price_eur") is not None:
            key = listing.get("source_search") or "unknown"
            self.data["price_history"].setdefault(key, []).append(float(listing["price_eur"]))

    def add_draft(self, draft: dict[str, Any]) -> None:
        self.data["drafts"].append(draft)
        self.data["drafts"] = self.data["drafts"][-200:]

    def add_run(self, summary: dict[str, Any]) -> None:
        self.data["runs"].append(summary)
        self.data["runs"] = self.data["runs"][-100:]

    def reference_price(self, search_name: str, configured: float | None = None) -> float | None:
        values = self.data["price_history"].get(search_name, [])[-100:]
        if len(values) >= 3:
            values = sorted(values)
            return values[len(values) // 2]
        return configured

    def prune(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.keep_days)
        for key, value in list(self.data["seen"].items()):
            try:
                if datetime.fromisoformat(value["first_seen"]) < cutoff:
                    self.data["seen"].pop(key, None)
                    self.data["decisions"].pop(key, None)
            except (KeyError, ValueError, TypeError):
                pass

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
