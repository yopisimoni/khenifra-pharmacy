import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        key = os.environ.get("GOOGLE_MAPS_EMBED_KEY", "")
        body = ("window.KHENIFRA_GOOGLE_MAPS_KEY = " + __import__('json').dumps(key) + ";").encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/javascript; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
