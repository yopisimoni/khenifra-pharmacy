"""Audit an owner-supplied CSV locally without publishing source records.
Usage: python3 scripts/audit_local_roster.py /path/to/private.csv
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

REQUIRED = ('التاريخ', 'اسم الصيدلية', 'الهاتف', 'العنوان', 'بداية الحراسة')

def audit(path):
    with open(path, encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        missing = [col for col in REQUIRED if col not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f'Missing required columns: {missing}')
        rows = list(reader)
    issues = []
    identities = {}
    for index, row in enumerate(rows, 1):
        name = row['اسم الصيدلية'].strip()
        phone = row['الهاتف'].strip()
        address = row['العنوان'].strip()
        if not name or not phone or not address:
            issues.append((index, name or '(empty)', 'Missing name/phone/address'))
        numbers = [re.sub(r'\D', '', item) for item in re.split(r'\s*/\s*', phone)]
        if any(len(number) != 10 or not number.startswith('0') for number in numbers):
            issues.append((index, name, 'Invalid phone format'))
        if name in identities and identities[name] != (phone, address):
            issues.append((index, name, 'Inconsistent repeated identity'))
        identities.setdefault(name, (phone, address))
        if row['بداية الحراسة'].strip() not in {'21:00', '21:30'}:
            issues.append((index, name, 'Unexpected duty start time'))
    number_owners = defaultdict(set)
    for name, (phone, _) in identities.items():
        for number in re.split(r'\s*/\s*', phone):
            number_owners[re.sub(r'\D', '', number)].add(name)
    for number, owners in number_owners.items():
        if len(owners) > 1:
            issues.append((0, ', '.join(sorted(owners)), 'Same number, different pharmacy'))
    return rows, identities, issues

if __name__ == '__main__':
    rows, identities, issues = audit(Path(sys.argv[1]))
    print(f'rows={len(rows)} unique_names={len(identities)} findings={len(issues)}')
    for index, name, reason in issues:
        print(f'row={index} pharmacy={name} finding={reason}')
    print('Historical local-data audit, NOT live Vercel, French name or exact GPS verification.')
    if issues:
        sys.exit(1)
