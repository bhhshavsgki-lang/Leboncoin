from __future__ import annotations

import json
import os
from openai import OpenAI

SCHEMA = {
    "type": "object",
    "properties": {
        "recommendation": {"type": "string", "enum": ["notify", "watch", "reject", "manual_check"]},
        "ai_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "risk_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "estimated_fair_price_eur": {"type": ["number", "null"]},
        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
        "reasoning_summary": {"type": "string"},
        "questions_for_seller": {"type": "array", "items": {"type": "string"}},
        "message_draft_fr": {"type": "string"}
    },
    "required": ["recommendation", "ai_score", "risk_score", "estimated_fair_price_eur", "confidence", "reasoning_summary", "questions_for_seller", "message_draft_fr"],
    "additionalProperties": False
}

SYSTEM = """Tu es un analyste prudent de bonnes affaires entre particuliers en France. Analyse l'annonce, le budget, la distance et l'historique fourni. Ne garantis jamais l'authenticité. Cherche les incohérences, prix anormalement bas, demandes de paiement hors plateforme et informations manquantes. Recommande notify seulement si l'opportunité paraît réellement intéressante et le risque raisonnable. Le brouillon doit être poli, court, en français, sans lien de paiement ni promesse. Pose des questions utiles (facture, état, numéro de série, remise en main propre). Retourne uniquement le JSON demandé."""


def judge(listing: dict, search: dict, fast: dict, reference_price: float | None, model: str, escalation_model: str) -> dict:
    client = OpenAI()
    payload = {"listing": listing, "search": search, "fast_analysis": fast, "reference_price_eur": reference_price}
    chosen = escalation_model if fast["fast_score"] >= 80 else model
    extra = {"reasoning": {"effort": "high"}} if chosen.startswith("gpt-5") else {}
    response = client.chat.completions.create(
        model=chosen,
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        response_format={"type": "json_schema", "json_schema": {"name": "deal_decision", "strict": True, "schema": SCHEMA}},
        max_completion_tokens=1800,
        extra_body=extra,
    )
    return json.loads(response.choices[0].message.content)
