# Location Demo Data Mode Prompt

Temporarily make the passenger map-first booking flow usable while backend services are not running.

Create a dedicated demo data folder under `client/lib/features/location/data/` and centralize deterministic UI fixtures there. Use these fixtures for pickup/dropoff geocoding, route preview, ride creation, and hybrid bidding-session discovery.

The real backend fetch blocks must remain available behind a clear demo switch so they can be activated quickly when the backend is available again. The temporary mode must not alter the production contract decisions:

- Passenger ride booking uses `HYBRID` for offer-style flows.
- `FIXED` ride creation support remains available through the existing city ride payload builder.
- The client must not introduce passenger-facing `BID_BASED` behavior.
- Mapbox remains only for map rendering; demo data replaces SafarPay backend responses, not direct Mapbox APIs.

Update the plan, decisions log, and client context files so future agents know the location feature is intentionally using temporary local demo responses.
