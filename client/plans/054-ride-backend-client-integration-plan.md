# Ride Backend Client Integration Plan

## Summary

Restore real backend execution paths for the passenger ride and HYBRID bidding flow while keeping the existing demo fixtures behind `SAFARPAY_USE_LOCATION_DEMO_DATA`.

## Implementation

- Add demo-mode gating to Ride, Bidding, Location, Geospatial, Ride WebSocket, Bidding WebSocket, and live Location WebSocket repositories.
- Route non-demo HTTP calls through `SHttpClient` with the existing service enum and auth token handling.
- Route non-demo WebSocket calls through `SApiConstants.websocketUri` with `?token=<access_token>`.
- Subscribe to Bidding sessions after opening the passenger or driver bidding socket.
- Parse backend ride lifecycle events including `DRIVER_LOCATION_UPDATED`.
- Parse backend bidding socket envelopes using either `data` or `payload`.
- Keep driver lifecycle and proof APIs available through repositories, but do not expand UI scope in this pass.

## Tests

- Add socket parser tests for backend ride and bidding envelopes.
- Add a repository test proving demo mode still returns fixtures.
- Run targeted location tests.
- Run Flutter analyzer and report unrelated existing findings separately.

## Runtime

For physical device testing use:

```bash
flutter run ^
  --dart-define=SAFARPAY_USE_LOCATION_DEMO_DATA=false ^
  --dart-define=SAFARPAY_AUTH_BASE_URL=http://192.168.100.3:8001/api/v1/auth ^
  --dart-define=SAFARPAY_RIDE_BASE_URL=http://192.168.100.3:8008/api/v1 ^
  --dart-define=SAFARPAY_BIDDING_BASE_URL=http://192.168.100.3:8002/api/v1/bidding ^
  --dart-define=SAFARPAY_LOCATION_BASE_URL=http://192.168.100.3:8003/api/v1/location ^
  --dart-define=SAFARPAY_GEOSPATIAL_BASE_URL=http://192.168.100.3:8006/api/v1 ^
  --dart-define=SAFARPAY_VERIFICATION_BASE_URL=http://192.168.100.3:8005/api/v1/verification ^
  --dart-define=MAPBOX_ACCESS_TOKEN=<your-mapbox-token>
```

## Notes

- Ride, Bidding, and Location sockets remain separate because each backend service owns a separate event contract.
- HYBRID ride creation depends on Kafka-backed bidding session creation; the client should continue using the existing session lookup retry behavior after creating a ride.
