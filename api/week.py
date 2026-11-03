import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler

NAMES = {
    "JABOR": "صيدلية جابور",
    "TOUHAMI": "صيدلية التوهامي",
    "AMALOU": "صيدلية أمالو",
    "NAJAH": "صيدلية النجاح",
    "HAMRIA": "صيدلية الحمرية",
    "ANASR": "صيدلية النصر",
    "NAJD": "صيدلية نجد",
    "GHRISSI": "صيدلية الغريسي",
    "NOUVELLE": "الصيدلية الجديدة",
    "KARAWIA": "الصيدلية القروية",
    "IBN ROCHD": "صيدلية ابن رشد",
    "TAZART IAARADAN": "صيدلية تزارت إعراضن",
    "HABRI": "صيدلية الحبري",
    "RACHID": "صيدلية الرشيد",
    "AFILAL": "صيدلية أفيلال",
    "EL WAHDA": "صيدلية الوحدة",
    "EL OMRANE": "صيدلية العمران",
    "WALILI": "صيدلية وليلي",
    "AJDIR": "صيدلية أجدير",
    "AGUELMAM": "صيدلية أكلمام",
    "ZERKTOUNI": "صيدلية الزرقطوني",
    "ALIAE": "صيدلية العلياء",
    "SAHAT DE COURSE": "صيدلية ساحة الكورس",
    "HOPITALE": "صيدلية المستشفى",
    "CHAAB": "صيدلية الشعب",
    "HEY EL FILAHI": "صيدلية الحي الفلاحي",
}
WEEK_TO_NIGHT = {
    "JABOR": "صيدلية جبور",
    "TOUHAMI": "صيدلية التهامي",
    "AMALOU": "صيدلية أمالو",
    "NAJAH": "صيدلية النجاح",
    "HAMRIA": "صيدلية حمرية",
    "ANASR": "صيدلية النصر",
    "GHRISSI": "صيدلية الغريسي",
    "NOUVELLE": "الصيدلية الجديدة",
    "KARAWIA": "صيدلية القروية",
    "IBN ROCHD": "صيدلية ابن رشد",
    "TAZART IAARADAN": "صيدلية نزارت إعراضن",
    "EL OMRANE": "صيدلية العمران",
    "AJDIR": "صيدلية أجدير",
    "AGUELMAM": "صيدلية أكلمام",
    "ZERKTOUNI": "صيدلية الزرقطوني",
    "SAHAT DE COURSE": "صيدلية ساحة الكورس",
    "HOPITALE": "صيدلية المستشفى",
    "CHAAB": "صيدلية الشعب",
    "HEY EL FILAHI": "صيدلية الحي الفلاحي",
}
def current_week_pharmacy(key, index, lookup):
    data = lookup.get(WEEK_TO_NIGHT.get(key, ""), {})
    # Original pharmacist duty source establishes the weekly appointment;
    # the night-order directory supplies contact details, not weekly hours.
    name_fr = data.get("nameFr") or "Pharmacie " + key.title()
    approved = json.loads(os.environ.get("VERIFIED_PHARMACY_PLACES_JSON", "{}"))
    candidate = approved.get(WEEK_TO_NIGHT.get(key, ""), {})
    place_id = candidate.get("placeId", "") if isinstance(candidate, dict) else ""
    return {
        "placeId": place_id,
        "locationVerified": bool(place_id),
        "id": "week-" + str(index),
        "name": key,
        "nameAr": NAMES.get(key, key),
        "nameFr": name_fr,
        "phone": data.get("phone", ""),
        "address": data.get("address", ""),
        "verified": False,
        "source": "CRPOS weekly schedule; contact details from supplied local pharmacy directory",
    }

def get_current_week(now=None):
    now = now or datetime.now(ZoneInfo("Africa/Casablanca"))
    date = now.date().isoformat()
    raw = os.environ.get("WEEKLY_ROTATION_JSON", "[]")
    try:
        entries = json.loads(os.environ.get("NIGHT_ROTATION_JSON", "[]"))
        lookup = {entry["nameAr"]: entry for entry in entries if entry.get("nameAr")}
    except (ValueError, TypeError, KeyError):
        lookup = {}
    for start, end, first, second in json.loads(raw):
        if start <= date <= end:
            return {
                "start": start, "end": end,
                "pharmacies": [
                    current_week_pharmacy(first, 1, lookup),
                    current_week_pharmacy(second, 2, lookup)
                ]
            }
    return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            payload = json.dumps({"week": get_current_week()}, ensure_ascii=False).encode("utf-8")
            status = 200
        except Exception:
            payload = b'{"error":"Duty schedule unavailable"}'
            status = 503
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
