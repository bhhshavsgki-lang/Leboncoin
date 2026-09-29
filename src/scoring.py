from __future__ import annotations

import math
import re
from .models import Listing


def distance_km(lat1, lon1, lat2, lon2) -> float | None:
    if None in (lat1, lon1, lat2, lon2):
        return None
    radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)


def fast_score(listing: Listing, search: dict, home: dict) -> dict:
    text = f"{listing.title} {listing.description}".lower()
    score, risk, reasons = 0, 0, []
    price = listing.price_eur
    max_price = search.get("max_price_eur")
    reference = search.get("reference_price_eur")
    if price is not None and max_price and price <= max_price:
        score += 20
        reasons.append("sous le budget")
    if price is not None and reference and reference > 0:
        discount = (reference - price) / reference
        if discount >= 0.30: score += 35; reasons.append("prix très inférieur à la référence")
        elif discount >= 0.15: score += 25; reasons.append("prix inférieur à la référence")
        elif discount >= 0.05: score += 10
        if discount < -0.20: risk += 10
    distance = distance_km(listing.latitude, listing.longitude, home.get("latitude"), home.get("longitude"))
    if distance is not None:
        if distance <= 20: score += 15; reasons.append("proche")
        elif distance <= home.get("max_distance_km", 50): score += 8
        else: risk += 35
    for word in search.get("must_have", []):
        if word.lower() in text: score += 8
        else: risk += 8
    for word in search.get("avoid", []):
        if word.lower() in text: risk += 18; reasons.append(f"signal à vérifier: {word}")
    if listing.image_urls: score += 5
    if listing.description and len(listing.description) >= 80: score += 5
    if not listing.description: risk += 8
    suspicious = re.findall(r"\b(urgent|cadeau|western union|hors plateforme|paiement avant|envoi uniquement)\b", text)
    risk += min(30, 8 * len(suspicious))
    return {"fast_score": min(100, score), "risk_score": min(100, risk), "distance_km": distance, "reasons": reasons}
