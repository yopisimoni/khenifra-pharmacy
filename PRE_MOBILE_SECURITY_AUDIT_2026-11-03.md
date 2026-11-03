# Khénifra Pharma — Pre-mobile security, data & localization audit
**Date:** 2026-11-03 (Africa/Casablanca)  
**Repository:** yopisimoni/khenifra-pharmacy  
**Target:** Vercel public website → future Android/iOS  
**Verdict:** **NO-GO for store release.** Safe to continue controlled QA.  
**Scope:** GitHub source inspection + connected Vercel metadata + GitHub Actions tests. This is **not** a penetration test, independent geolocation attestation or real device test. External anonymous access could not be fully exercised.

## Confirmed strengths
- Source is in GitHub; duty data is read server-side from Vercel **sensitive** environment variables (`WEEKLY_ROTATION_JSON`, `NIGHT_ROTATION_JSON`). The full rotation is not hard-coded in the public HTML.
- Night rotation is 40 entries, anchored at 2026-11-03, with coverage across midnight; returns current relevant entry only.
- Maps browser key is held in Vercel environment (not committed); note it is **intentionally exposed to the browser** by `/config.local.js`. Referrer and API restrictions in Google Cloud remain unverified.
- Current HTTP API returns JSON with `no-store` and `nosniff`, and errors do not include secrets.
- Frontend escapes most directory strings before HTML insertion. No account/password flows or public pharmacy editing endpoint were found in the inspected source.
- All **78 core translation keys** and **10 supplemental translation keys** appear in Arabic, French and English. Text correctness and layout are not verified by this key-parity check.
- GitHub Actions workflow on the review branch **passed**: Python tests, compile, frontend JavaScript syntax, translation parity, key-presence check.

## P0: must correct or verify before public mobile release
1. **Share-link identity collision (fixed in draft PR #1, not production):** previous `week-1`, `week-2`, `night-current` IDs can point to another pharmacy after a duty change. Use stable pharmacy IDs, then test old links.
2. **Time accuracy (fixed in draft PR #1):** frontend previously used visitor-device local time. Use `Africa/Casablanca` throughout; refresh schedule on returning from background. Verify behavior at 09:00, 21:00, 21:30 and midnight and on daylight-time changes.
3. **Unconfirmed site accessibility:** Vercel project metadata shows deployment protection enabled on `*.vercel.app` URLs. Test from an anonymous browser with no account; verify API and map scripts before claiming the service is publicly accessible. Do not weaken project protection without an explicit decision.
4. **Pharmacy location verification:** 0 Google Place IDs are approved in the connected environment. Unconfirmed pins must remain search results, not exact navigation destinations. Cross-check name + address + phone with local sources and obtain owner confirmation where ambiguous.
5. **Schedule confidence:** weekly source stops 2027-01-31; annual notice needs refresh workflow. Night rotation is based on user-confirmed 40-entry loop and may change administratively. Keep a dated source, last-confirmed date and manual correction procedure. Never claim an official night timetable if only a recurrence assumption is available.
6. **Store identity/regulatory readiness:** maintain independent-guide disclaimer; avoid portraying the app as the pharmacists' council or a regulated authority. Verify Google Play health-app declaration, privacy and Apple healthcare requirements as applicable.

## P1: implement/test before Android/iOS store submission
7. **Public privacy URL absent:** privacy is a modal in `index.html`, but there is no stand-alone public, non-editable `/privacy` or `privacy.html` page suitable for app store listing. Verify actual handling of location, Vercel requests and feedback email; review AR/FR/EN texts.
8. **Browser security headers:** production had `nosniff` and referrer policy but no explicit frame/permission policy; draft PR #1 adds `X-Frame-Options: DENY` and `Permissions-Policy`. Strong Content Security Policy is still pending because app uses inline script and styles; test third-party embeds before enforcing.
9. **Map key restrictions:** Google Cloud project settings were not accessible in this audit. Verify HTTP referrers, Maps Embed API-only restriction, billing alerts and quota; never confuse an environment variable with a server-secret key.
10. **Native experience:** current app lacks manifest/service worker checks in main HTML and has not passed iOS/Android real-device UX tests. An iOS WebView-only repackaging may fail Apple's minimum-functionality review. Plan meaningful native interaction (location permission, deep-link navigation, native share, offline state).
11. **Accessibility/SEO:** no reduced-motion media query, no `<main>`, and no meta description in inspected HTML. Test VoiceOver/TalkBack, large text, keyboard navigation, contrast and 320–430px widths.
12. **Localization:** static translation-key parity is PASS, but French/English privacy paragraphs are shorter than Arabic; review legal equivalence, Arabic bidi handling for French names, phones, dates and 2027 messages.
13. **Stale documentation:** `README.md` still describes `NIGHT_SCHEDULE_CSV_B64` rather than the actual `NIGHT_ROTATION_JSON`; update after finalizing APIs.
14. **Error and feedback experience:** feedback opens `mailto:`, which can fail on devices with no configured email app. Display an alternate contact method and avoid promising successful submission. Test empty/error API states on mobile.
15. **Owner workflow:** document who reviews reports, who can approve edits, how changes are versioned, and how quickly emergency corrections are published. The current user-report function does not automatically update pharmacy data.

## P2: follow-up improvements
- Replace duplicated hard-coded pharmacy-name mappings (e.g. `JABOR` / `جبور` vs `جابور`, `TOUHAMI` / `التهامي` vs `التوهامي`) with a single reviewed identifier registry.
- Reduce splash animation for accessibility, add offline/error guidance and last-data-update timestamp.
- Add tests for holiday dates and no-holiday fallback, cross-year weekly expiration, mobile geolocation refusal, WhatsApp/phone rendering and stale share links.

## Review branch, no production merge
Draft PR: https://github.com/yopisimoni/khenifra-pharmacy/pull/1
- Stable pharmacy share IDs
- Morocco-local frontend date
- Refresh when returning to foreground
- Language validation fallback
- X-Frame-Options and Permissions-Policy
- Python boundary tests; JavaScript syntax, translation and secret-absence checks
- GitHub Actions **success** (run 41661274368; this is code-level QA, not live browser validation).

## Launch acceptance gates
- [ ] Anonymous user opens Vercel HTTPS from mobile data without developer login
- [ ] Weekly/night API tested across 40-day cycle, Moroccan date boundaries and expiry
- [ ] Pharmacy data verified against sources and every public **confirmed GPS** manually reviewed
- [ ] Correct caller and directions link for all live duty entries
- [ ] Arabic, French, English complete end-to-end screenshots and manual QA
- [ ] Public privacy policy, support link, legal owner and contact information
- [ ] Key restrictions, quotas, security headers, CSP & frontend injection tests
- [ ] Android and iOS hardware tests, accessibility, denied-location and offline scenarios
- [ ] App-store compliance reviewed, preview approved and production monitored

## Recommended branding
Keep **Khénifra Pharma** as the product name, and use **“by Amara AI Solutions”** as the maker credit. Of the proposed spellings, **Amara AI Solutions** is the clearest established English business/agency identity. Avoid “Amara Solution AI” or singular “Amara AI Solution”. A future broader umbrella could use **AMARA Solutions**, but that should not be changed casually during a launch. Verify brand/trademark availability and legal registration independently; do not imply an incorporated company if none exists.
