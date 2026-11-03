"""Local-only location audit. Never upload the generated review CSV to GitHub."""
import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import quote

FIELDS = ("name_ar", "phone", "address", "search_url", "status",
          "place_id", "evidence_url", "reviewer", "notes")

def prepare(source, destination):
    with open(source, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    unique = {}
    for item in rows:
        name = item["اسم الصيدلية"].strip()
        if name in unique:
            if unique[name]["phone"] != item["الهاتف"]:
                raise ValueError("Conflicting phone: " + name)
            continue
        address = item["العنوان"].strip()
        query = f"{name}, {address}, Khénifra Maroc"
        unique[name] = dict(name_ar=name, phone=item["الهاتف"], address=address,
                            search_url="https://www.google.com/maps/search/?api=1&query=" + quote(query),
                            status="PENDING", place_id="", evidence_url="",
                            reviewer="", notes=item.get("ملاحظات", ""))
    if not unique:
        raise ValueError("No pharmacy records")
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(unique.values())
    return len(unique)

def approve(source, name, place_id, evidence_url, reviewer):
    if not re.fullmatch(r"[A-Za-z0-9_-]{10,160}", place_id):
        raise ValueError("Invalid Place ID")
    if not evidence_url.startswith("https://") or not reviewer.strip():
        raise ValueError("Evidence HTTPS URL and reviewer are required")
    with open(source, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    matches = [row for row in rows if row["name_ar"] == name]
    if len(matches) != 1:
        raise ValueError("Name must identify exactly one pharmacy")
    matches[0].update(status="APPROVED", place_id=place_id,
                      evidence_url=evidence_url, reviewer=reviewer.strip())
    with open(source, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

def export(source, destination):
    with open(source, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    approved = {}
    for item in rows:
        if item["status"] == "APPROVED":
            if not all(item.get(k) for k in ("place_id", "evidence_url", "reviewer")):
                raise ValueError("Missing evidence for " + item["name_ar"])
            approved[item["name_ar"]] = {"placeId": item["place_id"]}
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(approved, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(approved)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    p = actions.add_parser("prepare")
    p.add_argument("source")
    p.add_argument("output")
    p = actions.add_parser("approve")
    p.add_argument("review_csv")
    for flag in ("name", "place-id", "evidence-url", "reviewer"):
        p.add_argument("--" + flag, required=True)
    p = actions.add_parser("export")
    p.add_argument("review_csv")
    p.add_argument("output")
    args = parser.parse_args()
    if args.action == "prepare":
        print("Prepared", prepare(args.source, args.output), "entries; no API calls made.")
    elif args.action == "approve":
        approve(args.review_csv, args.name, args.place_id,
                args.evidence_url, args.reviewer)
        print("Approved:", args.name)
    else:
        print("Exported", export(args.review_csv, args.output), "approved IDs.")

if __name__ == "__main__":
    main()
