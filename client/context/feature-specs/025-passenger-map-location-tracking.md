# Prompt: Passenger Map Location Tracking

Add the passenger-side map foundation for SafarPay. The Flutter client should render native Mapbox maps, read foreground device GPS, call backend-mediated location/geospatial APIs for geocoding and route preview, and consume the ride tracking WebSocket for active ride driver updates.

## Requirements

- Add Mapbox Flutter Maps SDK, device GPS, WebSocket, and degraded-connectivity dependencies.
- Keep Mapbox server APIs backend-only. The client may use a restricted public Mapbox token only for map rendering.
- Extend API constants and HTTP utilities so client repositories can call auth, location, geospatial, ride, bidding, and gateway services.
- Add typed location models for coordinates, addresses, route previews, and live ride locations.
- Add repositories for Location Service geocode/reverse/live-location reads, Geospatial Service route/validation/surge reads, Ride Service lifecycle entry points, Bidding Service passenger entry points, and Location Service ride tracking WebSocket events.
- Add a device location service that requests foreground location and exposes current/streaming coordinates without storing raw GPS history.
- Add reusable map widgets under `lib/common/widgets/maps`.
- Make Home search open a real passenger ride search flow.
- Add ride search, route preview, and live tracking screens as the first passenger map-enabled flow.

## Acceptance Criteria

1. Home search opens the ride search screen.
2. Ride search can derive pickup from current GPS reverse geocode and search dropoffs through the backend.
3. Route preview calls backend geospatial validation/routing and renders a Mapbox map wrapper with pickup/dropoff context.
4. Ride tracking connects to the backend Location Service WebSocket with JWT query auth and handles driver location, ping, pong, error, and disconnect states.
5. Flutter analyzer has no new warnings/errors from this feature; unrelated pre-existing analyzer info items may remain.
