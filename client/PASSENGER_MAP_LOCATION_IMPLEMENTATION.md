# Passenger Map And Live Ride Implementation Notes

This document explains the passenger-side Mapbox, device GPS, backend geospatial, ride creation, and live ride tracking work added to the Flutter client.

## High-Level Result

The client now has a first passenger map foundation:

1. Home search opens a real ride planning flow.
2. The app can derive pickup from foreground device GPS.
3. Dropoff search is routed through the backend Location Service geocode endpoint.
4. Route preview is routed through backend Geospatial Service validation and route calculation.
5. Ride confirmation builds a backend-compatible fixed city ride request and calls Ride Service.
6. Live ride tracking connects to Location Service WebSocket using JWT query-token auth.
7. Native Mapbox rendering is isolated in reusable common map widgets.

The client does not call Mapbox Geocoding, Directions, Matrix, or Search APIs directly. Those remain backend-owned. Flutter uses Mapbox only for map rendering with a restricted public token.

## Dependencies Added

Updated `client/pubspec.yaml`:

- `mapbox_maps_flutter`: native Mapbox map rendering on Android/iOS.
- `geolocator`: foreground device location reads and streams.
- `web_socket_channel`: Location Service ride-tracking WebSocket connection.
- `connectivity_plus`: added for degraded/offline UX foundations. It is not deeply wired yet, but it is available for follow-up resilience work.

`flutter pub get` updated:

- `client/pubspec.lock`
- `client/macos/Flutter/GeneratedPluginRegistrant.swift`
- `client/windows/flutter/generated_plugin_registrant.cc`
- `client/windows/flutter/generated_plugins.cmake`

Those generated plugin registrant updates are expected because new Flutter plugins were added.

## Runtime Configuration

### Mapbox Token

The app reads the client Mapbox token from compile-time environment:

```dart
String.fromEnvironment('MAPBOX_ACCESS_TOKEN')
```

Location:

- `client/lib/utils/constants/api_constants.dart`

Run with:

```bash
flutter run --dart-define=MAPBOX_ACCESS_TOKEN=pk.your_public_token
```

Build with:

```bash
flutter build apk --dart-define=MAPBOX_ACCESS_TOKEN=pk.your_public_token
```

Use a restricted public Mapbox token for the client. Do not use the backend/server Mapbox token.

### Backend Base URLs

`SApiConstants` now has service-specific base URLs:

- `authBaseUrl`
- `gatewayBaseUrl`
- `locationBaseUrl`
- `geospatialBaseUrl`
- `rideBaseUrl`
- `biddingBaseUrl`

Each can be overridden with `--dart-define`, for example:

```bash
flutter run \
  --dart-define=MAPBOX_ACCESS_TOKEN=pk.your_public_token \
  --dart-define=SAFARPAY_LOCATION_BASE_URL=http://10.0.2.2:8003/api/v1/location \
  --dart-define=SAFARPAY_GEOSPATIAL_BASE_URL=http://10.0.2.2:8006/api/v1 \
  --dart-define=SAFARPAY_RIDE_BASE_URL=http://10.0.2.2:8008/api/v1
```

## API Routing Changes

### `SApiService`

Added in:

- `client/lib/utils/constants/api_constants.dart`

New enum:

```dart
enum SApiService {
  auth,
  gateway,
  location,
  geospatial,
  ride,
  bidding,
}
```

This prevents every HTTP request from being forced through `authBaseUrl`.

### `SHttpClient`

Updated:

- `client/lib/utils/http/client.dart`

`get`, `post`, and `delete` now accept a service selector:

```dart
SHttpClient.post(
  '/geocode',
  service: SApiService.location,
  requiresAuth: true,
  body: {'address': address},
);
```

Existing auth calls still work because the default service remains `SApiService.auth`.

### WebSocket URL Builder

Added:

```dart
SApiConstants.websocketUri(...)
```

It converts HTTP base URLs to WebSocket URLs:

- `http` -> `ws`
- `https` -> `wss`

It is used for Location Service ride tracking:

```text
/api/v1/location/ws/rides/{ride_id}/track?token=<JWT>
```

## Location Domain Models

Created:

- `client/lib/features/location/domain/location_models.dart`

Models:

- `SCoordinate`
- `SAddressResult`
- `SRouteStep`
- `SRoutePreview`
- `SDriverLiveLocation`
- `SPassengerLiveLocation`
- `SLiveRideLocations`

Why these exist:

- Keep backend JSON parsing out of widgets.
- Normalize backend fields like `latitude` / `longitude` and live event aliases like `lat` / `lng`.
- Provide stable typed objects for controllers and UI.

Important behavior:

- `SCoordinate.fromJson` accepts both:
  - `latitude`, `longitude`
  - `lat`, `lng`
- `SAddressResult.fromJson` handles Location Service geocode/reverse response shape.
- `SRoutePreview.fromJson` handles Geospatial Service route response:
  - `distance_km`
  - `duration_minutes`
  - `polyline`
  - `steps`
- `SLiveRideLocations.fromJson` handles live ride location snapshots with optional driver/passenger objects.

## Data Layer

All new data/repository files live under:

- `client/lib/features/location/data/`

### `location_repository.dart`

Class:

- `SLocationRepository`

Methods:

- `geocode(String address)`
- `reverseGeocode(SCoordinate coordinate)`
- `getRideLocations(String rideId)`

Backend services called:

- `POST /geocode` on Location Service
- `POST /reverse` on Location Service
- `GET /rides/{rideId}/locations` on Location Service

All use `requiresAuth: true`.

### `geospatial_repository.dart`

Class:

- `SGeospatialRepository`

Methods:

- `calculateRoute(origin, destination)`
- `validatePickup(coordinate)`
- `getSurge(coordinate)`

Backend services called:

- `POST /routes` on Geospatial Service
- `POST /validate-pickup` on Geospatial Service
- `POST /surge` on Geospatial Service

This keeps route calculation and pickup validation backend-mediated.

### `ride_repository.dart`

Class:

- `SRideRepository`

Methods:

- `createRide(Map<String, dynamic> body)`
- `fetchRide(String rideId)`
- `cancelRide({rideId, reason})`
- `buildCityRideRequest({pickup, dropoff})`

`buildCityRideRequest` creates a backend-compatible fixed city ride payload:

- `service_type`: `CITY_RIDE`
- `category`: `MINI`
- `pricing_mode`: `FIXED`
- two stops:
  - `PICKUP`
  - `DROPOFF`
- `detail.service_type`: `CITY_RIDE`
- `passenger_payment_method`: `CASH`
- `auto_accept_driver`: `true`

This replaced the original placeholder tracking transition. Confirming a preview now calls Ride Service and uses the returned ride id.

### `bidding_repository.dart`

Class:

- `SBiddingRepository`

Methods:

- `getBidsForSession(String sessionId)`
- `acceptBid({sessionId, bidId})`
- `getCounterOffers(String sessionId)`

This is a foundation for passenger bidding screens. It is not yet connected to a visible screen in this implementation.

### `device_location_service.dart`

Class:

- `SDeviceLocationService`

Methods:

- `currentCoordinate()`
- `positionStream()`

Responsibilities:

- Verify location services are enabled.
- Request/check foreground location permission.
- Return current GPS coordinate.
- Stream live coordinates for active flows.

Policy:

- Foreground location only.
- No raw GPS history is persisted locally.
- Background location is intentionally not implemented.

### `mapbox_config.dart`

Class:

- `SMapboxConfig`

Responsibilities:

- Read `MAPBOX_ACCESS_TOKEN`.
- Initialize Mapbox SDK access token.
- Warn if token is missing.
- Block release-mode map rendering if token is unavailable.

Called from:

- `client/lib/main.dart`

## WebSocket Event Handling

Created:

- `client/lib/features/location/data/live_ride_socket_event.dart`
- `client/lib/features/location/data/live_ride_socket_repository.dart`

### Event Types

`SLiveRideSocketEventType` supports:

- `driverLocationUpdated`
- `ping`
- `pong`
- `error`
- `unknown`

### Driver Location Event

Expected backend event:

```json
{
  "event": "DRIVER_LOCATION_UPDATED",
  "timestamp": "...",
  "data": {
    "driver_id": "...",
    "lat": 31.52,
    "lng": 74.35,
    "heading": 180,
    "speed": 42.1
  }
}
```

The parser converts this into `SDriverLiveLocation`.

### WebSocket Repository

`SLiveRideSocketRepository.connect(rideId)`:

1. Reads access token from `STokenStorage`.
2. Builds Location Service WebSocket URI:

   ```text
   /ws/rides/{rideId}/track?token=<accessToken>
   ```

3. Redacts token in logs.
4. Connects using `WebSocketChannel`.
5. Parses incoming messages.
6. Responds to `ping` with `{"event":"pong"}`.

The backend requires query-token auth for mobile WebSockets, so this follows the documented backend exception.

## Reusable Map Widgets

Created:

- `client/lib/common/widgets/maps/map_models.dart`
- `client/lib/common/widgets/maps/map_view.dart`

### `SMapMarker`

Represents a map marker in UI state.

Types:

- `pickup`
- `dropoff`
- `driver`
- `passenger`

### `SMapView`

Wraps Mapbox `MapWidget`.

Inputs:

- `initialCenter`
- `markers`
- `route`
- `zoom`
- `isLoading`
- `errorMessage`
- `onRecenter`
- `onMapCreated`

Current behavior:

- Initializes Mapbox map centered on `initialCenter`.
- Enables Mapbox location component/puck.
- Shows a status pill with route distance/duration or marker count.
- Shows loading overlay.
- Shows recenter button.
- Shows controlled unavailable state if token is missing in release mode.

Important limitation:

- The current wrapper does not yet draw custom marker annotations or route polyline layers onto Mapbox. It establishes the reusable map shell and passes marker/route state through the API. The next visual increment should add annotation manager and polyline layer rendering inside this wrapper.

## Controllers

Created under:

- `client/lib/features/location/controllers/`

### `SRideSearchController`

File:

- `ride_search_controller.dart`

State:

- query text
- loading
- error message
- pickup address
- selected dropoff
- geocode results

Flow:

1. On init, calls `loadCurrentPickup`.
2. `loadCurrentPickup` reads GPS using `SDeviceLocationService`.
3. It reverse geocodes GPS through `SLocationRepository`.
4. User enters dropoff.
5. Input is debounced for 450 ms.
6. Backend geocode is called.
7. Results are shown in UI.
8. Selecting a result stores the dropoff and moves to preview if pickup exists.

Failure behavior:

- If GPS fails, user sees manual pickup/search guidance.
- If geocode fails, user sees unavailable/retry text.

### `SRidePreviewController`

File:

- `ride_preview_controller.dart`

State:

- pickup address
- dropoff address
- loading
- creating ride
- error message
- route preview
- pickup validity

Flow:

1. On init, validates pickup through Geospatial Service.
2. Calls Geospatial Service route calculation.
3. Stores route preview for UI.
4. On confirm, builds a fixed city ride payload.
5. Calls Ride Service `POST /rides`.
6. Returns the created ride id.

Failure behavior:

- Invalid pickup disables confirmation.
- Route failure shows route unavailable.
- Ride creation failure shows request failure.

### `SRideTrackingController`

File:

- `ride_tracking_controller.dart`

State:

- connection/loading status
- status message
- driver live location
- passenger live location
- marker list derived from driver/passenger state

Flow:

1. On init, fetches current ride locations from Location Service.
2. Connects to Location Service WebSocket.
3. Updates driver marker on `DRIVER_LOCATION_UPDATED`.
4. Starts a local passenger GPS stream.
5. Updates passenger marker from device GPS.
6. Closes socket and GPS stream on controller disposal.

Failure behavior:

- Snapshot failure falls back to waiting for live data.
- Socket error updates reconnecting/disconnected status.
- GPS stream errors are ignored for now to avoid breaking tracking UI.

Reconnect/backoff is not fully implemented yet. The controller has status handling, but a production reconnect loop should be a follow-up.

## Screens And User Flow

Created under:

- `client/lib/features/location/screens/`

### Home Search Entry

Updated:

- `client/lib/features/home/screens/home/home.dart`
- `client/lib/features/home/screens/widgets/searchbar.dart`

`SSearchContainer` now accepts:

```dart
onSearchPressed
```

Home passes:

```dart
onSearchPressed: () => Get.to(() => const RideSearchScreen())
```

This turns the existing Home search UI into the entry point for passenger ride planning.

### `RideSearchScreen`

File:

- `ride_search_screen.dart`

UI:

- App bar
- subtitle
- pickup card
- dropoff search input
- backend geocode results
- no-results/error/loading states

Flow:

1. Screen starts.
2. Controller tries to get current pickup.
3. User searches dropoff.
4. Result tap navigates to `RidePreviewScreen`.

### `RidePreviewScreen`

File:

- `ride_preview_screen.dart`

UI:

- Map preview area
- pickup/dropoff route summary
- confirm ride button

Flow:

1. Controller validates pickup and calculates route.
2. Map wrapper displays route/point summary.
3. User confirms.
4. Controller creates a backend ride.
5. On success, navigates to `RideTrackingScreen(rideId: createdRideId)`.

### `RideTrackingScreen`

File:

- `ride_tracking_screen.dart`

UI:

- Map tracking area
- status panel

Flow:

1. Controller loads ride location snapshot.
2. Connects to ride tracking WebSocket.
3. Driver updates adjust tracking markers.
4. Passenger location comes from local GPS stream.

### Legacy `SearchScreen`

Updated:

- `client/lib/features/home/screens/search/search.dart`

The previous file had stale imports and broken placeholder code. It is now a compatibility wrapper:

```dart
class SearchScreen extends RideSearchScreen {}
```

This prevents old references from breaking while making the new ride search screen canonical.

## Constants And Text

Updated:

- `client/lib/utils/constants/texts.dart`
- `client/lib/utils/constants/sizes.dart`

Added text for:

- ride search title/subtitle
- pickup/dropoff hints
- route preview
- confirm/requesting state
- tracking title/status

Added sizes for:

- route preview map height
- live tracking map height
- ride sheet radius

## Analyzer Cleanup

During final verification, analyzer reported existing info-level issues. Since they were small and some files had already been formatted, they were cleaned:

- `client/lib/utils/helpers/helpers.dart`
  - `Color.withOpacity` replaced with `withValues(alpha: ...)` inside `SHelperFunctions.withOpacity`.
- `client/lib/features/personalization/screens/settings/widgets/settings_profile_tile.dart`
  - direct `withOpacity` calls now use `SHelperFunctions.withOpacity`.
- `client/lib/utils/theme/custom_themes/checkbox_theme.dart`
  - `MaterialStateProperty` / `MaterialState` replaced with `WidgetStateProperty` / `WidgetState`.
- `client/lib/utils/logging/logger.dart`
  - deprecated `_logger.v` replaced with `_logger.t`.
- `client/lib/utils/constants/enums.dart`
  - dangling doc comments changed to normal comments.

These cleanup edits are not part of the map feature behavior, but they were required to get `flutter analyze` to a clean result.

## Documentation Files Added Or Updated

Added:

- `client/context/feature-specs/025-passenger-map-location-tracking.md`
- `client/plans/026-passenger-map-location-tracking-plan.md`

Updated:

- `client/AGENTS.md`
- `client/context/architecture.md`
- `client/context/project-overview.md`
- `client/context/progress-tracker.md`
- `client/plans/decisions-log.md`

The documentation now records:

- Mapbox is client-rendering only.
- Backend owns geocoding/routing/ETA.
- Passenger location is foreground-only.
- Raw GPS history is not persisted locally.
- New context and plan files exist for this feature.

## Tests Added

Created under:

- `client/test/location/`
- `client/test/utils/`

### `location_models_test.dart`

Covers:

- `SCoordinate` parsing backend and client coordinate key variants.
- `SAddressResult` parsing Location Service response.
- `SRoutePreview` parsing Geospatial route response.
- `SLiveRideLocations` parsing snapshot response.

### `live_ride_socket_event_test.dart`

Covers:

- Driver location WebSocket event parsing.
- Ping and pong event recognition.

### `ride_repository_test.dart`

Covers:

- Fixed city ride request payload shape for backend Ride Service.

### `api_constants_test.dart`

Covers:

- Service base URL resolution.
- WebSocket URL construction and query token preservation.

## Verification Run

Final verification commands:

```bash
flutter analyze
```

Result:

```text
No issues found!
```

```bash
flutter test
```

Result:

```text
10 tests passed
```

Some Flutter/Dart commands hung inside the sandbox. The successful verification runs were executed outside the sandbox after approval because Flutter needed access to SDK/cache files.

## Current Known Limitations

1. `SMapView` creates the Mapbox map and location puck but does not yet draw custom marker annotations or route polyline layers.
2. Ride tracking reconnect/backoff is not fully implemented; current handling updates status on socket errors/disconnects.
3. Passenger GPS is streamed locally during tracking, but no passenger location update is sent to backend because the client should not invent unsupported backend calls.
4. Bidding repository exists as a foundation but is not wired into visible screens.
5. `connectivity_plus` is available but not yet integrated into visible degraded/offline UI.
6. Full device testing was not run; Android/iOS validation with a real Mapbox token and running backend services is still required.

## Next Implementation Steps

1. Add Mapbox annotation manager support in `SMapView` for pickup, dropoff, driver, and passenger markers.
2. Add route polyline decoding/rendering in `SMapView`.
3. Add WebSocket reconnect with exponential backoff and stop conditions based on ride status.
4. Expand ride request UI for service category, payment method, fare, surge disclosure, and bidding mode.
5. Add passenger ride lifecycle screens after ride creation: matching, bidding, driver assigned, arriving, in progress, completed.
6. Add integration tests or widget tests for the ride search and preview screens once backend contracts stabilize.
