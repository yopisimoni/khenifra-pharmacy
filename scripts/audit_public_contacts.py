"""Read-only public duty audit. No credentials or personal data in logs."""
import json
import os
from urllib.request import Request, urlopen

BASE = os.environ.get("KHENIFRA_BASE_URL", "https://khenifra-pharmacy.vercel.app").rstrip("/")
def fetch(path):
    req = Request(BASE + path, headers={"User-Agent": "Khenifra-Data-Integrity/1.0"})
    with urlopen(req, timeout=20) as resp:
        if resp.status != 200:
            raise RuntimeError(f"{path} HTTP {resp.status}")
        return json.load(resp)

def main():
    issues = []
    week = fetch("/api/week/current").get("week")
    if not isinstance(week, dict):
        issues.append("current weekly schedule is unavailable")
    else:
        pharmacies = week.get("pharmacies")
        if not isinstance(pharmacies, list) or len(pharmacies) != 2:
            issues.append("expected exactly two weekly duty pharmacies")
        else:
            for p in pharmacies:
                key = p.get("id", "(unknown)")
                if not p.get("nameAr"): issues.append(f"{key}: missing identity")
                if not str(p.get("phone") or "").strip(): issues.append(f"{key}: missing phone")
                if not str(p.get("address") or "").strip(): issues.append(f"{key}: missing address")
                if p.get("phoneNeedsReview"): issues.append(f"{key}: phone needs review")
                if p.get("addressNeedsReview"): issues.append(f"{key}: address needs review")
    night = fetch("/api/night/current").get("pharmacy")
    if not isinstance(night, dict):
        issues.append("night pharmacy unavailable")
    else:
        if not night.get("nameAr"): issues.append("night pharmacy missing identity")
        if not night.get("phone"): issues.append("night pharmacy missing phone")
    for issue in issues: print("AUDIT FINDING:", issue)
    if issues: raise SystemExit(f"FAIL: {len(issues)} public data-integrity findings")
    print("PASS: current public schedule contact fields populated (not independently verified)")
if __name__ == "__main__":
    main()
