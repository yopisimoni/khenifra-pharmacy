# Khénifra Pharma: Data integrity and visitor analytics

## Current incident (2026-11-23)
NAJD was in weekly NAMES but absent from WEEK_TO_NIGHT, so the weekly endpoint could not join it to the local night-contact directory. This branch adds the mapping. It does **not** assert that a phone number exists in the production directory or that an external number is verified.

The Google search screenshot gave candidate numbers for "Pharmacie Ennajd": 05 35 38 34 95 / 06 24 82 05 50. **Do not publish either as verified without confirming that the weekly NAJD is the same business and checking a primary/owner source.** Do not confuse it with Pharmacie Najah or Parapharmacie Najd.

## Visitor measurement
- Create a GA4 property + Web stream for https://khenifra-pharmacy.vercel.app.
- Copy the **Measurement ID** (G-...) and replace the empty `GA4_ID` in `analytics.js`.
- GA4 requests run only after an affirmative analytics consent. Visitors who decline are not counted; analytics counts are estimates, not a record of individuals.
- QR URL: https://khenifra-pharmacy.vercel.app/?src=qr-share
- `qr_visit` event is sent when a visitor consents and the QR URL has `src=qr-share`.
- In GA4, check Realtime, Reports > Acquisition, and Events > qr_visit. GA4 event reports can be delayed. The parameter `source` is not automatically a GA4 traffic-source dimension.
- Recheck privacy policy and legal obligations before enabling analytics.
- Vercel analytics, if preferred, needs enabling through the Vercel dashboard and applicable integration.

## Release checks
- `python3 -m unittest discover -s tests -v`
- `node scripts/check_frontend.mjs`
- `python3 scripts/smoke_public.py`
- Verify live `/api/week/current` contains exactly two pharmacies for the active week; check each has identity, phone, address, contact verification flag and reasonable `tel:` link, recording missing/unverified values as review findings, **not autofilling**.
- Review screenshots on iPhone and Android; test 08:59/09:00 and 20:59/21:00 Morocco time; confirm GPS and navigation work.
- Match Vercel deployment SHA to reviewed Git commit before release. No production changes until explicit release approval.
