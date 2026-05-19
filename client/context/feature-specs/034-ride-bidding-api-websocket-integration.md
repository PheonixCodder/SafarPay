# Ride And Bidding API/WebSocket Integration Prompt

Connect the passenger map-first booking flow to the real Ride, Bidding, Location, and Geospatial backend contracts while preserving temporary demo data behind an explicit switch for UI testing.

The client must follow the existing SafarPay folder style: feature-owned repositories, controllers, models, and screen widgets stay under `lib/features/location`, reusable primitives stay under `lib/common`, and utility behavior stays under `lib/utils`.

Requirements:

- Wire Ride HTTP routes from `services/ride/ride/api/router.py`.
- Wire Bidding HTTP routes from `services/bidding/bidding/api/router.py`.
- Add typed parsers for backend ride and bidding response contracts.
- Add passenger and driver WebSocket repositories for Ride service channels.
- Add passenger and driver WebSocket repositories for Bidding service channels.
- Keep Location service ride tracking WebSocket separate from Ride lifecycle WebSocket.
- Passenger UI must expose `FIXED` and `HYBRID` only; do not expose passenger-facing `BID_BASED`.
- Keep demo fixtures available with `SAFARPAY_USE_LOCATION_DEMO_DATA=true`.
- Use real backend HTTP/WebSocket paths when `SAFARPAY_USE_LOCATION_DEMO_DATA=false`.
- Keep Mapbox usage limited to map rendering. Search, routes, ride state, bids, and live locations stay backend-mediated.

Acceptance:

- Ride creation, cancellation, lifecycle, stops, verification codes, proofs, nearby drivers, bidding sessions, bid acceptance, passenger counter-offers, and counter-offer acceptance have client repository methods.
- Ride and Bidding WebSocket event parsers are covered by tests.
- Backend response parsers are covered by tests.
- `flutter analyze --no-pub` and focused location tests pass.
