# Local authority CSV reconciliation (2026-11-24)

**Source:** user-supplied historical Arabic CSV, 2026-09-21 through 2026-11-01, 42 daily entries covering 40 unique pharmacies. The user reports that a local pharmacy manager confirms the listed phone numbers and street addresses. This is a source attestation, not verified production/GPS evidence.

## Local private-file audit
Run:
```bash
python3 scripts/audit_local_roster.py "/path/to/khenifra_night_pharmacies_2026-09-21_to_2026-11-01.csv"
python3 -m unittest discover -s tests -v
node scripts/check_frontend.mjs
```
On the supplied input: **42 rows, 40 distinct names, 0 missing phone/address, 0 inconsistent repeated identities, 0 shared numbers across different entries, 0 format issues**. Ten rows had start 21:30, the others 21:00. Do not infer the current rota's exact time from the historical rows.

## Explicit technical change
`api/night.py` previously suppressed phone `0661649124` for `صيدلية المسيرة الخضراء` because of a third-party directory conflict. User-supplied manager attestation supports retaining the provided phone, so the suppressor was removed. No records, coordinates, verified Places IDs, or live environment values were changed. This change affects only records already supplied to the service at runtime.

## Remaining blockers
1. `NIGHT_ROTATION_JSON` and `WEEKLY_ROTATION_JSON` are production secrets. This audit **did not compare their complete contents** to the user CSV; do so privately with authorized deployment access, without exporting their values into GitHub.
2. The uploaded historical CSV has **no French name column**. Cannot validate 40 French names from this CSV alone. Review `nameFr` against a separate authority reference and mark unverified names.
3. Six weekly keys remain unmatched in the 40-pharmacy night directory: HABRI, RACHID, AFILAL, EL WAHDA, WALILI, ALIAE. Do not invent mapping to different pharmacies. They require separate weekly contact source or a verified name match.
4. Exact GPS/entrances still need separate checks; keep unverified pins as text searches.
5. `api/week.py` has a provisional hard-coded Amalou contact, which is **not** present in this historical 40-pharmacy CSV. Do not assert that this CSV validates Amalou.

## Release
Review tests and preview, verify actual runtime contact values against owner-approved inputs, and merge only after approval. `VERIFIED_PHARMACY_PLACES_JSON` must not be populated from unverified map results.

## 2026-11-24 production endpoint observation
- `/api/week/current` returned two records for 2026-11-23..2026-11-29.
- `week-najd`: Arabic name present; French fallback `Pharmacie Najd`; phone and address empty. Its name is absent from the 40-row manager-confirmed night directory. Do **not** infer phone from public directories.
- `week-ghrissi`: phone `0535586232`, address `شارع محمد الخامس حي الحسن الثاني`; both match the manager-confirmed historical CSV. Exact GPS not verified.
- `/api/night/current`: `Nouvelle Pharmacie` / `الصيدلية الجديدة`, phone `0535586521`, address `زنقة وجدة 237 شارع محمد الخامس`, matches uploaded historical source.
- The owner-supplied 42-row CSV and 40-row French reference align on **all 40 Arabic names, phones and addresses**; the French reference contains 40 distinct nonempty labels. This confirms the two uploaded sources agree, not that the full Vercel environment matches.
- Historical shift start times: 32 records at 21:00 and 10 records at 21:30. Keep a public timing caveat; do not assert 21:00 applies to every duty.
- Missing contact mapping keys still need independently supplied approved weekly records: `HABRI`, `RACHID`, `AFILAL`, `EL WAHDA`, `WALILI`, `ALIAE`; current `NAJD` is also absent from the manager-confirmed night directory despite having a mapping key.

## Safe implementation
- Optional `WEEKLY_CONTACTS_JSON`: keyed by weekly rota identifier, providing explicit `nameFr`, `phone` and `address` from a manager-approved separate weekly source. Do not populate it with guesses.
- The old hard-coded provisional `AMALOU` phone was removed: records not in an approved contact source must remain visibly flagged as missing.
- No Vercel environment values were accessed or changed; no GPS or `placeId` was approved.
