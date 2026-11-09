# Data and navigation QA — 2026-11-09

Project: **Khénifra Pharma**, by **Amara AI Solutions**.

## User-reported defects and audited evidence

| Finding | Observed / cause | Corrective action | Remaining limitation |
|---|---|---|---|
| Weekly duty Pharmacie Amalou has no phone | `api/week.py` joins weekly keys against the private night rotation; Amalou is absent from that 40-pharmacy roster, so no contact data is obtained. | Flag `phoneNeedsReview` and show an explicit, translated missing-contact state instead of a blank field; do not fabricate a call link. | Owner/direct source must confirm identity and phone. |
| Pharmacie Amalou address missing | Same incomplete weekly-to-night contact join. | Flag `addressNeedsReview`, render review warning in weekly and map views. | An authoritative address still needed. |
| Three navigation choices appear before route origin | Original modal rendered Google/Waze/Apple immediately when opening. | Hide chooser until visitor supplies a starting address or actively grants geolocation; clear stale options when input changes. | Real mobile GPS permission UX needs device QA. |
| Unverified pins may look like exact routes | For unapproved pharmacies, map links are search results based on name/address. | Show explicit warnings and keep Google/Waze/Apple links as searches, never claim exact guidance. | Confirm each pharmacy's real pin independently or through owner. |
| Offline duty safety | PWA service worker stores only offline warning page. | Preserved. | Real device test pending. |
| Day/night visibility | Frontend uses Africa/Casablanca hour and 21:00/09:00 boundary. | Preserved; regression tests run. | Real 21:00 and 09:00 device test pending. |

## Amalou contact evidence (candidate, NOT approved for click-to-call)

Several external directories list **Pharmacie Amalou** at **87 bd Massira hay Amalou Ighriben**, phone **0535 58 73 44**:
- https://www.annuaire-gratuit.ma/pharmacies/pharmacie-amalou-s85942.html
- https://www.yelo.ma/company/198257/Pharmacie_Amalou
- https://khenifra.pharmacieenpermanence.ma/pharmacie-amalou
- https://sahha.ma/pharmacien/khenifra/pharmacie-amalou-khenifra

**Conflict:** https://medicament-maroc.com/pharmacies/khenifra also attributes 0535 58 73 44 to **Pharmacie Razi**. Other derived sites list Amalou with no phone and the less specific `Avenue Amalou` address. The same phone appearing across different pharmacy identities requires direct validation before making it a live call button. No GPS coordinate is promoted by this report. Multiple online aggregators may reproduce one underlying record, so this is NOT proof of independently confirmed identity.

## Private night-rotation inventory
The local owner-supplied 40-row audit file was scanned offline on 2026-11-09: 40 names, 0 repeated names, 0 missing `phone`, 0 missing `address`, 0 repeated nonblank phone within that particular file. This says nothing about the accuracy of those fields or the *weekly* source and does not prove that live production environment values match the file. Keep the private directory out of GitHub.

## Release acceptance
- PR CI must have successful Python unit tests, JS+translation checks and anonymous production smoke test.
- Anonymous endpoint smoke only checks HTTP/content structure, **not** the accuracy of all weekly contact details or GPS.
- Test Chrome Android and Safari iPhone with GPS permitted and denied, manually entered origin, close/reopen modal, and click each map provider.
- Do not infer an exact pharmacy entrance from a successful map embed search.
- Continue owner verification of disputed phone/address/GPS after release.
