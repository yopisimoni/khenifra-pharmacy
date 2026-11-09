# Khénifra Pharma — release gate and duty-state contract (2026-11-09)

**Release decision: NO-GO pending real-device verification.** A Vercel `READY` deployment or HTTP 200 is not a sufficient release gate.

## Source of truth and duty visibility
- Backend `/api/week/current`: official date-scoped weekly duty list (from production `WEEKLY_ROTATION_JSON`). Duty list must contain two entries while the configured current week is valid.
- Backend `/api/night/current`: 40-pharmacy cycle (from production `NIGHT_ROTATION_JSON`). Must return **non-null** dated pharmacy for duties after November 3, 2026, otherwise return HTTP 503 instead of an empty-success response.
- Browser date and duty window in `Africa/Casablanca`: weekly only on **09:00–20:59**, night only on **21:00–08:59** in active duty cards and map listings.
- The **weekly tab is hidden at night** and opening it programmatically redirects to night. The standalone night tab may show the *upcoming* night pharmacy during the day. A daytime weekly card must never include a night card.
- Weekly and night data are separate schedules, not interchangeable. The night list is only a *contact lookup* for weekly entries with matching name, not proof a weekly schedule has the right contact information.
- Before 09:00, night response must have *yesterday's Morocco duty date*. At/after 09:00, night response must have *today's Morocco duty date*; any mismatched response must be rejected.
- On transient network error, retain a **previously loaded and still date-valid** schedule only. Never retain yesterday's active night entry as today's, and never claim a missing rota is current.

## Regression coverage / evidence
- `node scripts/check_frontend.mjs`: test weekly success, error, expiry; test night success, null data, network error, stale previous date and out-of-order night requests. Test both hour boundary rules.
- `python3 -m unittest discover -s tests -v`: backend night rotation with before-09:00 previous-day behavior; missing night environment must fail explicitly.
- `python3 scripts/smoke_public.py`: anonymous production HTTP/content checks, **requiring** valid weekly entries during known source period and a non-null night pharmacy dated to the current Casablanca duty date. Logs must not reveal pharmacy directory or Maps credentials.
- PR: https://github.com/yopisimoni/khenifra-pharmacy/pull/7
- Incident: 2026-11-09 screenshots show inconsistent night tab vs. home and a short-lived missing weekly list, despite HTTP 200 backend requests. Exact root cause is not proven from read-only runtime logs.

## Remaining gates (not automatic)
1. Independently test at 08:59, 09:00, 20:59, 21:00 and around midnight in Chrome Android and Safari iPhone; verify homepage, weekly/night tabs, map listings, reload and background return.
2. Real GPS permission granted/denied and manually entered origin; verify Google Maps, Waze and Apple Maps navigation.
3. Inspect all weekly and night phone/address identity mismatches; keep `AMALOU` number unconfirmed until a primary or owner source settles conflict; no speculative GPS pin.
4. Verify Maps Embed browser-key restrictions, quota/budget, legal/privacy/accessibility and app-store compliance.
5. Record per-release deploy SHA, successful checks and screenshot evidence. One feature per PR, no direct production edits and no unsupported `DONE` labels.
6. Pharmacy owner corrections remain a separate review queue, not a blocker to building or testing features, but public data must not claim unverified details.

**Contacts/brand:** Khénifra Pharma, by Amara AI Solutions. simohamed.amara@gmail.com.
