from __future__ import annotations

import os
import requests


def format_alert(listing: dict, fast: dict, ai: dict, draft: str) -> str:
    return (f"BONNE AFFAIRE ({ai['ai_score']}/100, risque {ai['risk_score']}/100)\n"
            f"{listing['title']} — {listing.get('price_eur') or '?'} €\n"
            f"Distance: {fast.get('distance_km') or '?'} km\n"
            f"Pourquoi: {ai['reasoning_summary']}\n"
            f"Questions: {'; '.join(ai.get('questions_for_seller', []))}\n"
            f"Annonce: {listing['url']}\n\nBrouillon vendeur:\n{draft}")


def notify(text: str) -> None:
    sent = False
    token, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if token and chat:
        response = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat, "text": text}, timeout=20)
        response.raise_for_status(); sent = True
    webhook = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook:
        response = requests.post(webhook, json={"content": text[:1900]}, timeout=20)
        response.raise_for_status(); sent = True
    if not sent:
        print(text)
