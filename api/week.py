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
def get_current_week(now=None):
    now = now or datetime.now(ZoneInfo("Africa/Casablanca"))
    date = now.date().isoformat()
    raw = os.environ.get("WEEKLY_ROTATION_JSON", "[]")
    for start, end, first, second in json.loads(raw):
        if start <= date <= end:
            return {
                "start": start, "end": end,
                "pharmacies": [
                    {"id": "week-1", "name": first, "nameAr": NAMES.get(first, first), "phone": "", "address": "", "verified": False, "source": "CRPOS weekly duty schedule"},
                    {"id": "week-2", "name": second, "nameAr": NAMES.get(second, second), "phone": "", "address": "", "verified": False, "source": "CRPOS weekly duty schedule"}
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
