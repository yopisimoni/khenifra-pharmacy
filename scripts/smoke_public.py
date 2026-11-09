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
    ("/icons/icon-180.png", "image/png"),
    ("/icons/icon-192.png", "image/png"),
    ("/icons/icon-512.png", "image/png"),
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
    elif expected == "image/png":
        if ctype != expected:
            raise AssertionError(f"{path}: content type {ctype}")
        assert body[:8] == bytes.fromhex("89504e470d0a1a0a"), f"{path}: not a PNG (first 12 bytes hex: {body[:12].hex()}, length={len(body)})"
        size = int(path.rsplit("-", 1)[1].split(".", 1)[0])
        assert int.from_bytes(body[16:20], "big") == size, f"{path}: wrong width"
        assert int.from_bytes(body[20:24], "big") == size, f"{path}: wrong height"
    elif expected == "application/json":
        if ctype != expected:
            raise AssertionError(f"{path}: content type {ctype}")
        data = json.loads(body)
        key = "week" if path.startswith("/api/week") else "pharmacy"
        assert key in data, f"{path}: missing {key}"
        if key == "week":
            from datetime import datetime
            from zoneinfo import ZoneInfo
            today = datetime.now(ZoneInfo("Africa/Casablanca")).date().isoformat()
            # The weekly rota is stored in production for the period ending 2027-01-31.
            # If this period is active, an empty API response is a production defect.
            if "2026-11-09" <= today <= "2027-01-31":
                week = data["week"]
                assert isinstance(week, dict), f"{path}: empty weekly duty despite configured period, local date {today}"
                assert week.get("start", "") <= today <= week.get("end", ""), f"{path}: weekly duty dates do not include {today}"
                assert len(week.get("pharmacies", [])) == 2, f"{path}: expected two scheduled duty pharmacies"
                print(f"PASS {path}: current-week payload present for {today} ({len(week['pharmacies'])} pharmacies)")
    else:
        if ctype != expected:
            raise AssertionError(f"{path}: content type {ctype}")
        assert b"<html" in body.lower(), f"{path}: HTML not returned"
        if path == "/":
            assert b"Kh" in body and b"manifest.webmanifest" in body, f"{path}: app shell missing"
        if path == "/privacy.html":
            assert b'id="policy"' in body, f"{path}: policy content missing"
    print(f"PASS {path}: HTTP {status} {ctype} (anonymous)")

if __name__ == "__main__":
    for route, mime in CHECKS:
        check(route, mime)
