from __future__ import annotations

import json
from pathlib import Path
from .input_reader import read_input_ads
from .models import utc_now
from .storage import StateStore
from .scoring import fast_score
from .notifiers import format_alert, notify


def load_config() -> dict:
    path = Path("config/settings.json")
    if not path.exists():
        path = Path("config/settings.example.json")
    return json.loads(path.read_text(encoding="utf-8"))


def find_search(listing, searches):
    text = f"{listing.title} {listing.description}".lower()
    if listing.source_search:
        for search in searches:
            if search["name"] == listing.source_search:
                return search
    for search in searches:
        keywords = search.get("keywords", [])
        if not keywords or any(keyword.lower() in text for keyword in keywords):
            listing.source_search = search["name"]
            return search
    return None


def simple_decision(fast: dict, reference_price: float | None, listing: dict) -> dict:
    fair_price = reference_price
    price = listing.get("price_eur")
    discount = ((fair_price - price) / fair_price * 100) if fair_price and price else 0
    recommendation = "notify" if fast["fast_score"] >= 45 and fast["risk_score"] <= 35 else "watch"
    return {
        "recommendation": recommendation,
        "ai_score": fast["fast_score"],
        "risk_score": fast["risk_score"],
        "confidence": 100,
        "estimated_fair_price_eur": fair_price,
        "reasoning_summary": "; ".join(fast["reasons"]) or "Aucun signal particulier",
        "questions_for_seller": ["Le produit est-il toujours disponible ?", "Avez-vous une facture ou une preuve d'achat ?"],
        "message_draft_fr": "Bonjour, votre article est-il toujours disponible ? Est-il possible de le voir et de vérifier son état avant l'achat ?",
        "discount_percent": round(discount, 1),
    }


def run() -> None:
    cfg = load_config()
    decision_cfg = cfg["decision"]
    store = StateStore(keep_days=decision_cfg.get("keep_state_days", 90))
    listings = read_input_ads("data/input_ads.json", decision_cfg.get("max_ads_per_run", 30))
    processed, saved = 0, 0
    for listing in listings:
        if store.seen(listing.id):
            continue
        search = find_search(listing, cfg["searches"])
        if not search:
            continue
        listing_dict = listing.as_dict()
        fast = fast_score(listing, search, cfg["location"])
        reference = store.reference_price(search["name"], search.get("reference_price_eur"))
        decision = simple_decision(fast, reference, listing_dict)
        store.mark_seen(listing_dict, decision)
        processed += 1
        if decision["recommendation"] == "notify":
            store.add_draft({"at": utc_now(), "listing_id": listing.id, "url": listing.url, "message": decision["message_draft_fr"]})
            notify(format_alert(listing_dict, fast, decision, decision["message_draft_fr"]))
            saved += 1
    store.add_run({"at": utc_now(), "read": len(listings), "processed": processed, "saved": saved})
    store.prune()
    store.save()
    print(json.dumps({"read": len(listings), "processed": processed, "saved": saved}, ensure_ascii=False))


if __name__ == "__main__":
    run()
