# Place Search & Pin Address Labels Plan (086)

## Summary

Fix two related location problems seen in production logs and ride search UX:

1. **Mapbox `422` on `/places/search`** — forward geocode is called with a coordinate string (`31.53723, 74.42631`) instead of a place name; Mapbox rejects it; fallback returns empty while the API still responds `200`.
2. **Pickup/dropoff fields show coordinates after map-pin confirm** — `confirmMapPin()` → `reverseGeocode()` → `selectAddress()` copies `result.formatted` into the search controllers; when reverse geocode fails or returns a coordinate fallback, the compose sheet shows lat/lng instead of a human-readable name.

Backend and client changes are required. This plan is numbered **086** and pairs with feature spec `context/feature-specs/086-place-search-and-pin-address-labels.md` (create when implementing).

---

## Symptoms (observed)

| Symptom | Log / UI evidence |
|--------|-------------------|
| Mapbox errors in location container | `Mapbox search_places_rich failed ... 422 Unknown` for URL path `.../mapbox.places/31.53723%2C%2074.42631.json` |
| Search still “succeeds” | `POST /api/v1/location/places/search` → `200`, often empty Mapbox fallback |
| Pin selection shows coords | Pickup/dropoff `SLocationInputBar` `value` is `pickup?.formatted` / `dropoff?.formatted` after `SBookingMapControls` pin confirm |
| Coordinate re-search loop | User (or debounced search) can type/paste the coordinate string → triggers Mapbox forward again → repeated `422` |

---

## Root causes

### A. Wrong Mapbox API for coordinate-shaped queries (backend)

`SearchPlacesUseCase` falls back to `MapboxClient.search_places_rich(query)`, which uses **forward** geocoding:

```text
GET /geocoding/v5/mapbox.places/{query}.json
```

Forward geocode expects **text** (street, POI, city). A string like `31.53723, 74.42631` is not valid forward input → **HTTP 422**. The client catches the exception and returns `[]`, so the user sees no Mapbox results.

**Note:** `latitude` / `longitude` on the search request are only used for **local** PostGIS search today; they are **not** passed to Mapbox as `proximity`.

### B. Reverse geocode / API returns coordinate `formatted` (backend + client)

`MapboxClient.reverse_geocode()` uses a fallback when the API fails or returns no features:

```python
formatted=f"{latitude:.5f}, {longitude:.5f}"
```

`ReverseGeocodeUseCase` may also return early from `nearest_place` with stored data, or save-through only when `addr.street` is set — so some valid Mapbox responses with `place_name` but weak `street` still degrade to coordinate text.

On the client, `selectAddress()` always does:

```dart
pickupSearchController.text = result.formatted;
```

There is no **display label** that prefers `street`, `city`, or `place_name` over a coordinate-shaped `formatted` string.

### C. Compose UI binds directly to `formatted` (client)

[booking_sheet.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/screens/ride_search/widgets/booking_sheet.dart) passes `pickup?.formatted` / `dropoff?.formatted` into [location_input_bar.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/screens/ride_search/widgets/location_input_bar.dart). Any bad `formatted` from pin confirm, GPS pickup load, or search selection appears in the chip.

Flow for pin confirm:

```text
SBookingMapControls (pin) → SRideSearchController.confirmMapPin()
  → mapController.centerCoordinate()
  → SLocationRepository.reverseGeocode()
  → selectAddress() → pickupSearchController.text = result.formatted
```

---

## Target behavior

| Scenario | Expected |
|----------|----------|
| User searches “Gulberg” | Local DB first; Mapbox forward with `proximity` bias when lat/lng sent |
| User searches / pastes `31.52, 74.35` | **No** forward geocode 422; treat as coordinates (reverse geocode or single result), never put coords in forward URL |
| User confirms map pin | Pickup/dropoff show **place name** (e.g. street + city), not `lat, lng` |
| Reverse geocode fails | Show clear error on pin confirm; do **not** write coordinate string into search field as if it were an address |
| Debounced search after pin | Must not re-fire Mapbox forward with coordinate text from the field |

---

## Implementation

### Phase 1 — Backend (location service)

**1. Coordinate-shaped query guard**

- Add `location/maps/query_detection.py` (or similar) with `looks_like_coordinates(query: str) -> tuple[float, float] | None` (regex for `lat, lng` / `lng, lat`, sensible bounds).
- In `SearchPlacesUseCase.execute()`:
  - If query parses as coordinates → **skip** `search_places_rich`.
  - Option A: call `reverse_geocode(lat, lng)` and return one `PlaceSearchResult` (high confidence).
  - Option B: return empty list and rely on client to use `/reverse` (prefer **Option A** for consistency).

**2. Mapbox forward: pass `proximity`**

- Extend `MapboxClient.search_places_rich(query, *, limit, country, proximity: tuple[float, float] | None)`.
- When `SearchPlacesUseCase` has `latitude` / `longitude`, add query param `proximity={lng},{lat}` (Mapbox order) per [Geocoding API](https://docs.mapbox.com/api/search/geocoding/#forward-geocoding).
- Wire from `PlaceSearchRequest` through use case (already has lat/lng).

**3. Harden reverse geocode response**

- In `ReverseGeocodeUseCase` / `MapboxClient.reverse_geocode`:
  - Prefer `place_name` for `formatted` when present.
  - Save-through: save when `place_name` or `street` exists, not only `addr.street`.
- Avoid persisting coordinate-only `formatted` into `location.places` (would pollute local search).

**4. Logging**

- For expected bad forward queries (coordinate guard hit): log **INFO**, not ERROR stack trace.
- On Mapbox 422: log response body once at WARNING (helps future debugging).

**5. Config / ops (document only)**

- Ensure `MAPBOX_ACCESS_TOKEN` in the container is a **server** token from env, not committed defaults.
- Do not log full token in URLs (redact in log formatter if needed).

**Files**

- `services/location/location/infrastructure/mapbox_client.py`
- `services/location/location/application/use_cases.py`
- `services/location/location/domain/interfaces.py` (if protocol signature changes)
- New: `services/location/location/maps/query_detection.py` (optional small module)
- Tests: `services/location/tests/` — coordinate guard, proximity param, reverse label

---

### Phase 2 — Client (Flutter)

**1. Display label helper**

- Add `SAddressResult.displayLabel` (extension or method on `location_models.dart`):
  - If `formatted` is **not** coordinate-like → use `formatted`.
  - Else build from `[street, city, country].whereType().join(', ')`.
  - Else fallback: `'Selected location'` (never show raw coords in UI).
- Add `bool get isCoordinateLikeFormatted` (shared regex with backend rules).

**2. Use display label everywhere user-visible text is set**

- [ride_search_controller.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/controllers/ride_search_controller.dart):
  - `selectAddress`, `selectRecentDropoff`, `loadCurrentPickup` success path → `pickupSearchController.text = result.displayLabel`.
  - `confirmMapPin`: after reverse geocode, if `result.isCoordinateLikeFormatted` → set `errorMessage` and **do not** call `selectAddress` (or call with blocked UI state).
- [booking_sheet.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/screens/ride_search/widgets/booking_sheet.dart):
  - `SLocationInputBar` `value`: `pickup?.displayLabel ?? '...'` (or helper on controller).

**3. Search debounce guard**

- In `onSearchChanged` / `search()`: if trimmed query `isCoordinateLike` → skip `searchPlaces` OR call `reverseGeocode` once and show single result (align with backend Option A).

**4. Optional: structured fields from API**

- If backend adds `name` on `PlaceSearchResponse`, map to `SAddressResult` for richer labels (future-proof; not blocking).

**Files**

- `client/lib/features/location/domain/location_models.dart`
- `client/lib/features/location/controllers/ride_search_controller.dart`
- `client/lib/features/location/screens/ride_search/widgets/booking_sheet.dart`
- `client/lib/features/location/screens/ride_search/widgets/booking_search_results.dart` (title: `result.displayLabel`)
- Tests: `client/test/features/location/` — displayLabel, coordinate detection, confirmMapPin does not set coord text

---

### Phase 3 — Verification

**Manual (ride search screen)**

1. Open ride search with real location API (`SAFARPAY_USE_LOCATION_DEMO_DATA=false`).
2. Confirm map pin on a known address → pickup/dropoff show **street/city**, not `31.xx, 74.xx`.
3. Type a place name → results appear; no `422` in location container logs.
4. Paste `31.53723, 74.42631` in search → no ERROR spam; sensible result or empty message (no crash).
5. After pin confirm, edit search field — debounced search must not re-trigger coordinate forward 422.

**Automated**

```bash
# Backend (from repo root)
pytest services/location/ -k "search or reverse or mapbox" -v

# Client
cd client && flutter analyze lib/features/location/
cd client && flutter test test/features/location/
```

**Log check**

- No `search_places_rich failed ... 422` for coordinate paths after fix.
- `served_from=MAPBOX_FALLBACK` only for real text queries.

---

## Task checklist

| # | Task | Layer | Priority |
|---|------|--------|----------|
| 1 | Coordinate query detection + branch in `SearchPlacesUseCase` | Backend | P0 |
| 2 | `proximity` on `search_places_rich` | Backend | P1 |
| 3 | Reverse geocode `formatted` / save-through quality | Backend | P1 |
| 4 | `SAddressResult.displayLabel` + coordinate detector | Client | P0 |
| 5 | `confirmMapPin` reject coordinate-only reverse | Client | P0 |
| 6 | Compose sheet + search results use `displayLabel` | Client | P0 |
| 7 | Search debounce guard for coordinate-like input | Client | P1 |
| 8 | Tests + manual QA per Phase 3 | Both | P1 |

---

## Out of scope (086)

- Mapbox token rotation / contract storage policy (handled operationally).
- Re-indexing entire `location.places` table for bad historical rows (optional cleanup migration later).
- Changing map camera / controls (completed in **085**).

---

## Dependencies

- **085** map camera & controls (done) — pin confirm UX depends on reliable reverse geocode labels.
- Location service running with valid `MAPBOX_ACCESS_TOKEN` and PostGIS `location.places` migrated.

---

## Success criteria

- Zero Mapbox `422` errors for coordinate-shaped `/places/search` queries under normal pin + search flows.
- After map-pin confirm, pickup and dropoff fields show human-readable labels in [ride_search_screen.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/screens/ride_search/ride_search_screen.dart) compose mode.
- Search-by-name still returns local + Mapbox results with proximity bias when GPS/pickup is known.
