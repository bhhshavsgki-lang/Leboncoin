from __future__ import annotations

import json
import os
from pathlib import Path
from .email_reader import read_alerts
from .models import utc_now
from .storage import StateStore
from .scoring import fast_score
from .ai_judge import judge
from .notifiers import format_alert, notify


def load_config() -> dict:
    path = Path(os.getenv("CONFIG_PATH", "config/settings.json"))
    if not path.exists(): path = Path("config/settings.example.json")
    return json.loads(path.read_text(encoding="utf-8"))


def find_search(listing, searches):
    text = f"{listing.title} {listing.description}".lower()
    for search in searches:
        if not search.get("keywords") or any(k.lower() in text for k in search["keywords"]):
            listing.source_search = search["name"]
            return search
    return None


def run() -> None:
    cfg = load_config(); decision_cfg = cfg["decision"]
    store = StateStore(keep_days=decision_cfg.get("keep_state_days", 90))
    listings = read_alerts(decision_cfg.get("max_ads_per_run", 30))
    processed, notified = 0, 0
    for listing in listings:
        if store.seen(listing.id): continue
        search = find_search(listing, cfg["searches"])
        if not search: continue
        listing_dict = listing.as_dict()
        fast = fast_score(listing, search, cfg["location"])
        reference = store.reference_price(search["name"], search.get("reference_price_eur"))
        if fast["fast_score"] < 20 or fast["risk_score"] > 65:
            ai = {"recommendation": "reject", "ai_score": fast["fast_score"], "risk_score": fast["risk_score"], "reasoning_summary": "Filtre rapide défavorable", "questions_for_seller": [], "message_draft_fr": "", "estimated_fair_price_eur": reference, "confidence": 70}
        else:
            ai_cfg = cfg["ai"]
            ai = judge(listing_dict, search, fast, reference, ai_cfg["model"], ai_cfg["escalation_model"])
        store.mark_seen(listing_dict, ai)
        processed += 1
        if ai["recommendation"] == "notify" and ai["ai_score"] >= decision_cfg["minimum_ai_score"] and ai["risk_score"] <= decision_cfg["maximum_risk_score"]:
            store.add_draft({"at": utc_now(), "listing_id": listing.id, "url": listing.url, "message": ai["message_draft_fr"]})
            if os.getenv("DRY_RUN", "0") != "1": notify(format_alert(listing_dict, fast, ai, ai["message_draft_fr"]))
            else: print(format_alert(listing_dict, fast, ai, ai["message_draft_fr"]))
            notified += 1
    store.add_run({"at": utc_now(), "read": len(listings), "processed": processed, "notified": notified})
    store.prune(); store.save()
    print(json.dumps({"read": len(listings), "processed": processed, "notified": notified}, ensure_ascii=False))


if __name__ == "__main__": run()
