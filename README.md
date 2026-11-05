# Khénifra Pharma

Independent local duty-pharmacy guide for Khénifra, Morocco, published by **Amara AI Solutions**. Web first, with future Android and iOS releases.

## Deployment
- Vercel project: `khenifra-pharmacy`
- Production: https://khenifra-pharmacy.vercel.app
- Privacy: https://khenifra-pharmacy.vercel.app/privacy.html
- PWA: `/manifest.webmanifest`, `/icons/pharmacy.svg`, `/sw.js`, `/offline.html`.
- Production should be publicly accessible; preview deployments retain Vercel Authentication.
- The offline worker **never caches active duty information, maps, or API responses**. Offline users get a warning instead of stale pharmacy details.

## Runtime environment (Vercel)
- `NIGHT_ROTATION_JSON` (sensitive, production): private 40-item pharmacy schedule, starting November 3, 2026. Night duty is calculated in `Africa/Casablanca`.
- `WEEKLY_ROTATION_JSON` (sensitive, production): source-backed weekly rota, reviewed regularly.
- `GOOGLE_MAPS_EMBED_KEY` (sensitive at rest): a browser Maps Embed key served to the page. **The key is public to visitors by design** and therefore must be restricted in Google Cloud by authorized HTTPS referrers and Maps Embed API only.
- Optional `VERIFIED_PHARMACY_PLACES_JSON` (sensitive, production): manually approved Google Places IDs, never speculative coordinates.

The server endpoints `/api/night/current` and `/api/week/current` return only the relevant current entries. Do not publish the full source CSV or environment values.

## Duty display
The browser uses the **Africa/Casablanca** time zone:
- 09:00–20:59: weekly duty card(s).
- 21:00–08:59: **only the night-duty pharmacy** is displayed in duty and map views.
- Night duty uses nominal hours 21:00–09:00; some pharmacies start at 21:30, so visitors are advised to call before travelling.
- View refreshes on visibility return and checks period changes every 30 seconds.

**Important:** This is an independent directory, not an official healthcare authority. Source schedules and pharmacy coordinates can change. Contact the pharmacy before visiting. Ambiguous map pins remain searches, not confirmed GPS routes. Corrections from owners require review.

## Local checks
```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q api scripts tests
node scripts/check_frontend.mjs
```
GitHub Actions config: `.github/workflows/pre-mobile-qa.yml`.

## Remaining release gates
1. Independently verify anonymous external access to homepage, privacy page and endpoints.
2. Test live map, call and share links on Android and iOS hardware; test geolocation denied and no network.
3. Verify Google Cloud key restrictions, budgets and API enablement.
4. Approve iOS/Android PNG home-screen icons; current manifest uses an SVG icon and this may not meet every platform's icon expectations.
5. Review localization and accessibility screenshots in AR, FR, EN.
6. Track night/weekly source validity and owner-reported corrections. Do not claim unconfirmed GPS is verified.
7. Complete platform privacy and app-store compliance review before native submission.
