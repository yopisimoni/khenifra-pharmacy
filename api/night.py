import os, base64, csv, io, json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler

def get_duty(now=None):
    now = now or datetime.now(ZoneInfo('Africa/Casablanca'))
    encoded = os.environ.get('NIGHT_SCHEDULE_CSV_B64', '')
    if not encoded:
        return None
    try:
        raw = base64.b64decode(encoded, validate=True).decode('utf-8-sig')
        records = csv.DictReader(io.StringIO(raw))
        for r in records:
            dt = r['التاريخ']
            start = datetime.fromisoformat(dt + 'T' + r['بداية الحراسة']).replace(tzinfo=ZoneInfo('Africa/Casablanca'))
            end = datetime.fromisoformat(dt + 'T' + r['نهاية الحراسة (صباح اليوم التالي)']).replace(tzinfo=ZoneInfo('Africa/Casablanca'))
            if end <= start: end += timedelta(days=1)
            if start <= now < end or (now.date().isoformat()==dt and now < start):
                return {'id':'night-current','date':dt,'nameAr':r['اسم الصيدلية'],'name':r['اسم الصيدلية'],'phone':r['الهاتف'],'address':r['العنوان'],'startTime':r['بداية الحراسة'],'endTime':r['نهاية الحراسة (صباح اليوم التالي)'],'verified':False,'upcoming':now<start,'source':'برنامج الحراسة المقدم من المستخدم'}
    except (ValueError, KeyError, UnicodeError, TypeError) as e:
        raise RuntimeError('Invalid private schedule configuration') from e
    return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            body=json.dumps({'pharmacy':get_duty()},ensure_ascii=False).encode('utf-8')
            status=200
        except Exception:
            body=b'{"error":"Schedule unavailable"}'
            status=503
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)
