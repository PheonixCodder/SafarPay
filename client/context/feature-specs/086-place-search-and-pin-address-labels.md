# Place Search & Pin Address Labels (086)

## Prompt

Fix Mapbox `422` errors when place search receives coordinate-shaped queries, and fix pickup/dropoff fields showing `31.53723, 74.42631` instead of place names after confirming a location with the map pin control on ride search.

## Requirements

### 1. Backend: no forward geocode for coordinates

- Detect lat/lng strings in `/places/search` query.
- Route them to reverse geocode (or equivalent), not `search_places_rich` forward API.
- Pass `proximity` to Mapbox forward geocode when the client sends latitude/longitude for text queries.

### 2. Backend: better reverse geocode labels

- Prefer `place_name` / structured fields over coordinate fallback text when Mapbox succeeds.
- Do not persist coordinate-only rows into `location.places`.

### 3. Client: human-readable labels after pin confirm

- Map pin flow (`SBookingMapControls` → `confirmMapPin`) must show street/city in pickup/dropoff fields, not raw coordinates.
- Use a shared `displayLabel` on `SAddressResult`; reject coordinate-only reverse results with a user-visible error.

### 4. Client: search field hygiene

- Debounced search must not send coordinate-shaped text to forward place search (avoids repeated 422s).

## Plan

See [086-place-search-and-pin-address-labels-plan.md](../../plans/086-place-search-and-pin-address-labels-plan.md).
