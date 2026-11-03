import json
import os
from datetime import date, datetime, time, timedelta
from http.server import BaseHTTPRequestHandler
from zoneinfo import ZoneInfo

CASABLANCA = ZoneInfo("Africa/Casablanca")
ANCHOR = date(2026, 11, 3)
CYCLE_LENGTH = 40

def get_duty(now=None):
    now = now or datetime.now(CASABLANCA)
    if now.tzinfo is None:
        now = now.replace(tzinfo=CASABLANCA)
    local_now = now.astimezone(CASABLANCA)
    duty_date = local_now.date()
    # Before 09:00, show the shift that started the previous evening.
    if local_now.time() < time(9, 0):
        duty_date -= timedelta(days=1)
    if duty_date < ANCHOR:
        return None
    raw = os.environ.get("NIGHT_ROTATION_JSON", "")
    if not raw:
        return None
    records = json.loads(raw)
    if len(records) != CYCLE_LENGTH:
        raise RuntimeError("Night rotation must contain exactly 40 entries")
    index = (duty_date - ANCHOR).days % CYCLE_LENGTH
    row = records[index]
    if not row.get("nameAr") or not row.get("nameFr"):
        raise RuntimeError("Incomplete night rotation entry")
    return {
        "id": "night-current",
        "date": duty_date.isoformat(),
        "name": row["nameFr"],
        "nameAr": row["nameAr"],
        "nameFr": row["nameFr"],
        "phone": row.get("phone", ""),
        "address": row.get("address", ""),
        "startTime": "يُرجى التأكيد",
        "endTime": "09:00",
        "verified": False,
        "upcoming": local_now.date() == duty_date and local_now.time() < time(21, 30),
        "source": "دورة الحراسة الليلية المكونة من 40 صيدلية - تحتاج تأكيد التوقيت",
        "locationNeedsReview": bool(row.get("locationNeedsReview", False)),
        "scheduleBasedOnRotation": True
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            payload = json.dumps({"pharmacy": get_duty()}, ensure_ascii=False).encode("utf-8")
            status = 200
        except Exception:
            payload = b'{"error":"Night rotation unavailable"}'
            status = 503
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
