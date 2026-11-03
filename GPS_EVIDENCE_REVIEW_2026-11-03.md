# Pharmacy map evidence review — 2026-11-03

**Public GPS routing: 0/40 approved. The site's existing name/address map search remains the safe fallback.**

A private 40-row evidence file was prepared and remains outside GitHub. In this research pass:
- 1 candidate has **independent close map agreement**: Jabbour (published directory versus OpenStreetMap / Mapcarta coordinates approximately 6 m apart). Not entrance/owner verified.
- 10 candidates have a coordinate from **one** matching directory. Not independently confirmed.
- 2 candidates have a material **conflict** and must remain blocked: Touhami (two published points approximately 1.83 km apart); Alfath (matching phone but conflicting street descriptions).
- 27 roster entries remain **not individually verified with GPS sources**; do not treat these as absent from maps.

Selected sources (candidate data, not official verification):
- Jabbour: https://www.annuaire-gratuit.ma/pharmacies/pharmacie-jabbour-s54792.html and https://mapcarta.com/fr/N8458142174
- Touhami: https://www.annuaire-gratuit.ma/pharmacies/pharmacie-touhami-s54823.html and https://mapcarta.com/fr/N8458146207
- Alfath: https://www.annuaire-gratuit.ma/pharmacies/pharmacie-alfath-s54764.html
- Other directory candidates: https://www.annuaire-gratuit.ma/pharmacies/_khenifra

Do not release a candidate coordinate as a confirmed navigation destination. For verified destination, require a reviewed pharmacy listing/place identifier and check against physical building or owner-supplied pinned location; if sources disagree, require owner or on-site confirmation.

**Status:** no changes to `VERIFIED_PHARMACY_PLACES_JSON`; no navigation coordinates published; no paid Places API requests made.

The private evidence CSV belongs in the owner's private project workspace, not in this public repository.
