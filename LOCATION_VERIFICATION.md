# Location verification / التحقق من مواقع الصيدليات

**Status: candidate discovery, not approved GPS.**

The browser Maps Embed API displays maps but does not establish a verified pharmacy entrance. Use this process before adding exact routing.

1. Keep the user-supplied official pharmacy CSV outside the public GitHub repository.
2. Run:
   `python3 scripts/location_audit.py prepare '/path/to/night.csv' '/private/pharmacy_location_review.csv'`
3. Open each Google Maps search URL in the output and verify the pharmacy name, phone, street, and physical pin. If the name is ambiguous or the pin is wrong, ask the pharmacy for its Maps share link.
4. Only after **human review**, execute:
   `python3 scripts/location_audit.py approve '/private/pharmacy_location_review.csv' --name 'صيدلية التهامي' --place-id 'VERIFIED_GOOGLE_PLACE_ID' --evidence-url 'https://...' --reviewer 'Admin'`
5. Run:
   `python3 scripts/location_audit.py export '/private/pharmacy_location_review.csv' '/private/approved-places.json'`
6. Store JSON in Vercel **sensitive Production** environment variable `VERIFIED_PHARMACY_PLACES_JSON`. Redeploy. The API returns a Place ID only for the pharmacy currently on duty. **Do not commit JSON or the full CSV**.

Google Maps uses approved `destination_place_id` for precise location lookup. Waze/Apple Maps remain text searches until their coordinates are independently verified.

This workflow does not call Places API or incur usage charges. A paid Places search may be added later only with explicit authorization, a Google Cloud API restriction and a budget cap. Google's Places API requires field masks and its own usage/pricing terms.

**Review priorities** (all pending approval):
- Jabbour: name, street and phone corroborated in independent directories, but coordinates vary.
- Touhami: matching Google listing appears, but exact entrance has not been confirmed.
- Al Massira Al Khadra: similarly named pharmacies create an identity-collision risk.

Do not label any position 'GPS verified' until its location is reviewed. This is not verification of an active duty shift or opening hours.
