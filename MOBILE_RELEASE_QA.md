# Mobile QA / Release Gate

Status: **web QA in progress; Android/iOS native builds not yet approved**.

## Automated checks
- GitHub Actions: `.github/workflows/pre-mobile-qa.yml` verifies backend unit tests, JavaScript syntax, localization parity, 21:00/09:00 Morocco boundaries, PWA files and offline warning.
- `scripts/smoke_public.py` sends **anonymous** read-only HTTP requests to the production hostname:
  - `/`
  - `/privacy.html`
  - `/manifest.webmanifest`
  - `/api/week/current`
  - `/api/night/current`
- The script checks HTTP 200 and required content structure, logging **route and status only**, never full returned pharmacy data or map credentials.
- All code checks must pass after the latest commit. Vercel READY alone does not prove anonymous browser access.

## Manual Android test matrix
1. Open using Chrome on mobile data, with no GitHub/Vercel session. Verify homepage and pharmacy card, then privacy page.
2. Use Chrome **Add to Home Screen / Install App**. Check launch, viewport, SVG icon, no address bar where supported.
3. Switch between Arabic, French and English; confirm layout alignment, menu, notification and feedback text.
4. Verify tap-to-call, Google Maps, Waze, Apple Maps links as supported, and denial of geolocation.
5. Check map correction contact action uses `simohamed.amara@gmail.com` and never auto-publishes map corrections.
6. Turn off data and refresh: show **offline warning**, never a cached active pharmacy.
7. Verify 20:59 day, 21:00 night only, 08:59 night, 09:00 day, including the map view. Requires controlled clock/time mocking or actual boundary test; do not change server duty schedule.

## Manual iPhone test matrix
1. Use Safari on mobile data, without authentication. Verify viewport, safe areas, scroll, buttons and privacy link.
2. Use **Share → Add to Home Screen**. Confirm launch and safe-area rendering.
3. Check native app icon (apple-touch-icon PNG still requires integration into repo), splash, status bar and correct standalone navigation.
4. Switch all three languages and test VoiceOver, larger text and phone/map contact actions.
5. Deny location; verify no incorrect claim of precise GPS. Open third-party map chooser.
6. Turn off connectivity: show offline warning rather than outdated duty data.
7. Cross-check 09:00/21:00 transitions in Casablanca time.

## Current blockers
- Public routes need a verified **successful external smoke run**; Vercel deployment is not enough.
- Browser map key restrictions must be confirmed in Google Cloud (HTTPS referrers, Maps Embed API only, quota/billing).
- SVG-only icon is not sufficient for robust iOS/Android installation; PNG assets 180,192,512 were prepared outside repo and require adding to the versioned deployment.
- No hands-on Android/iPhone results or screenshots.
- The Apple/Google stores require platform compliance review and a reviewable native value proposition.
- Pharmacy GPS owner corrections stay a separate maintenance track. No unverified pins should be promoted.

## Owner
Khénifra Pharma, **by Amara AI Solutions**. Public contact: **simohamed.amara@gmail.com**.
