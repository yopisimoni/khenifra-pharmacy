# Khénifra Pharma — HTTPS preview candidate

Contains the public UI and serverless endpoints only. No night-duty CSV or API key is included.

## Vercel settings (preview environment)
- `GOOGLE_MAPS_EMBED_KEY`: Google Maps Embed browser key, restricted in Google Cloud to the HTTPS preview hostname and Maps Embed API. The key is visible to browsers; protect using referrer/API restrictions.
- `NIGHT_SCHEDULE_CSV_B64`: base64-encoded private CSV, stored in Vercel's protected environment variable (not committed). Configure it using the Vercel dashboard.

Until the private schedule variable is configured, the night API returns `null`, not a made-up pharmacy. Do not publish this preview as a verified duty service.

## GitHub
Only commit the files in this directory. Never commit `setup/night_schedule.csv`, `config.local.js`, or your Desktop env folder.

## After deployment
Verify `/api/night/current` returns only one record (or null). Check `config.local.js` executes; test language switches and the navigation chooser; then test mobile HTTPS.
