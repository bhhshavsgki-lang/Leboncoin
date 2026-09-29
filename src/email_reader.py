from __future__ import annotations

import email
import imaplib
import os
import re
from email.header import decode_header
from bs4 import BeautifulSoup
from .models import Listing


def text_part(message) -> str:
    chunks = []
    parts = message.walk() if message.is_multipart() else [message]
    for part in parts:
        if part.get_content_type() not in ("text/plain", "text/html"): continue
        raw = part.get_payload(decode=True) or b""
        charset = part.get_content_charset() or "utf-8"
        value = raw.decode(charset, errors="replace")
        chunks.append(BeautifulSoup(value, "html.parser").get_text(" ") if part.get_content_type() == "text/html" else value)
    return "\n".join(chunks)


def decode_subject(value: str) -> str:
    return "".join((part.decode(charset or "utf-8", errors="replace") if isinstance(part, bytes) else part) for part, charset in decode_header(value or ""))


def read_alerts(limit: int = 30) -> list[Listing]:
    host = os.getenv("IMAP_HOST") or "imap.gmail.com"
    port = int(os.getenv("IMAP_PORT") or "993")
    user = os.getenv("IMAP_USERNAME")
    password = os.getenv("IMAP_PASSWORD")
    if not user or not password:
        raise RuntimeError("IMAP_USERNAME and IMAP_PASSWORD must be configured in GitHub Secrets")
    box = imaplib.IMAP4_SSL(host, port)
    box.login(user, password); box.select("INBOX")
    status, data = box.search(None, '(UNSEEN FROM "leboncoin")')
    ids = data[0].split()[-limit:]
    results = []
    for msg_id in ids:
        _, raw = box.fetch(msg_id, "(RFC822)")
        message = email.message_from_bytes(raw[0][1])
        body = text_part(message)
        urls = list(dict.fromkeys(re.findall(r"https?://[^\s<>]+", body)))
        urls = [u.rstrip(".,)") for u in urls if "leboncoin.fr" in u]
        if not urls: continue
        price_match = re.search(r"(\d[\d\s]*)(?:,\d+)?\s*€", body)
        location_match = re.search(r"(?:à|a)\s+([A-ZÀ-Ÿ][^\n,]{2,40})", body)
        results.append(Listing(title=decode_subject(message.get("Subject")), url=urls[0], price_eur=float(price_match.group(1).replace(" ", "")) if price_match else None, location=location_match.group(1).strip() if location_match else "", description=body[:5000], source_email_date=message.get("Date", "")))
        box.store(msg_id, "+FLAGS", "\\Seen")
    box.logout()
    return results
