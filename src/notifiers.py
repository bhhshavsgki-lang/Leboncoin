from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path


def format_alert(listing: dict, fast: dict, ai: dict, draft: str) -> str:
    questions = "\n".join(f"- {question}" for question in ai.get("questions_for_seller", [])) or "- Aucune question particulière générée"
    return (f"### {listing['title']}\n\n"
            f"- **Prix :** {listing.get('price_eur') or '?'} €\n"
            f"- **Distance :** {fast.get('distance_km') or '?'} km\n"
            f"- **Score :** {ai['ai_score']}/100\n"
            f"- **Risque :** {ai['risk_score']}/100\n"
            f"- **Confiance :** {ai.get('confidence', '?')}/100\n"
            f"- **Pourquoi :** {ai['reasoning_summary']}\n"
            f"- **Annonce :** [{listing['url']}]({listing['url']})\n\n"
            f"**Questions à poser au vendeur**\n{questions}\n\n"
            f"**Brouillon de message**\n\n> {draft.replace(chr(10), chr(10) + '> ')}\n")


def save_to_report(text: str) -> None:
    path = Path(os.getenv("DEALS_REPORT_PATH", "data/good_deals.md"))
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if not path.exists():
        path.write_text("# Bonnes affaires Leboncoin\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as report:
        report.write(f"\n---\n\n## Nouvelle analyse — {now}\n\n{text}\n")


def notify(text: str) -> None:
    save_to_report(text)
    print(f"Bonne affaire ajoutée au rapport: {os.getenv('DEALS_REPORT_PATH', 'data/good_deals.md')}")
