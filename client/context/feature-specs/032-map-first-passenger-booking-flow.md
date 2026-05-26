# Map-First Passenger Booking Flow Prompt

Create a passenger ride booking experience inspired by the provided inDrive references, but implemented in SafarPay's light theme and existing Flutter architecture.

The flow must open from the existing Home search entry and replace the current entry-level `RideSearchScreen` with a production-style map-first surface. The screen should be split into a full-screen Mapbox map background and a draggable overlay sheet where the passenger selects pickup, dropoff, service category, vehicle, and fare offer.

Pickup and dropoff must support both backend-powered search and map-pin selection. The client must not call Mapbox geocoding, directions, matrix, or search APIs directly; those remain backend-mediated through the existing Location and Geospatial repositories.

After pickup and dropoff are selected, calculate the route through the backend, render pickup/dropoff markers and a connecting route line on the map, and show route summary in the sheet. If backend route geometry is unavailable, the map can show a straight connector between the selected points while the backend-mediated route summary remains the source of distance and ETA. The next state should show vehicle/fare options similar to the inDrive offer screen, using SafarPay's light visual system.

Support the five passenger categories:
- Groceries
- City rides
- City to City
- Couriers
- Freight

Vehicle differentiation should mirror the product/category setup already used by driver registration planning, but owned by the passenger booking feature instead of importing driver registration models.

Ride creation should use backend `HYBRID` pricing. The backend must expose a bidding session id through ride creation or passenger ride WebSocket for production live-offer tracking. Until that exists, the UI must show a controlled matching state instead of faking live bids.

Follow the normalized client screen structure:
- one main screen file per screen folder.
- screen-local widgets under that screen's `widgets/` folder.
- reusable map widgets under `lib/common/widgets/maps`.
- shared helpers under `lib/utils`.

Update the implementation plan, architecture/progress context, and decisions log.
