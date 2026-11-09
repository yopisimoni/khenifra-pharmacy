"""Anonymous production smoke test; do not print map credentials or pharmacy directory data."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = os.environ.get("KHENIFRA_BASE_URL", "https://khenifra-pharmacy.vercel.app").rstrip("/")
CHECKS = [
    ("/", "text/html"),
    ("/privacy.html", "text/html"),
    ("/manifest.webmanifest", "application/manifest+json"),
    ("/api/week/current", "application/json"),
    ("/api/night/current", "application/json"),
]
def check(path, expected):
    req = Request(BASE + path, headers={"User-Agent": "KhenifraPharma-CI-Smoke/1.0", "Accept": "*/*"})
    try:
        with urlopen(req, timeout=15) as response:
            status = response.status
            ctype = response.headers.get("Content-Type", "").split(";", 1)[0].strip()
            body = response.read(500_000)
    except (HTTPError, URLError) as exc:
        raise AssertionError(f"{path}: request failed ({type(exc).__name__}; no response body logged)") from exc
    if status != 200:
        raise AssertionError(f"{path}: unexpected HTTP status {status}")
    if expected == "application/manifest+json":
        # Vercel may serve .webmanifest as application/manifest+json or application/json.
        if ctype not in ("application/manifest+json", "application/json"):
            raise AssertionError(f"{path}: content type {ctype}")
        data = json.loads(body)
        assert data["start_url"] == "/" and data["display"] == "standalone"
    elif expected == "application/json":
        if ctype != expected:
            raise AssertionError(f"{path}: content type {ctype}")
        data = json.loads(body)
        key = "week" if path.startswith("/api/week") else "pharmacy"
        assert key in data, f"{path}: missing {key}"
    else:
        if ctype != expected:
            raise AssertionError(f"{path}: content type {ctype}")
        assert b"<html" in body.lower(), f"{path}: HTML not returned"
    print(f"PASS {path}: HTTP {status} {ctype} (anonymous)")

if __name__ == "__main__":
    for route, mime in CHECKS:
        check(route, mime)
