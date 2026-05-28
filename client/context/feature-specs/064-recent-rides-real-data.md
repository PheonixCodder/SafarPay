# Recent Ride Destinations With Live ETA

## Prompt

Replace the static recent rides shown from the home search area with backend-backed passenger recent destinations. Show the same recent destination shortcuts in the ride booking sheet inside `_ComposeContent`, below the dropoff input and above the booking category strip.

Recent destinations must come from ride history, but the ETA shown beside each destination must be calculated live from the current pickup/current device location through the existing geospatial route API backed by Mapbox. Do not reuse historical trip duration.

When a recent destination is tapped from either location, set the ride-search dropoff to that destination's saved coordinates. From home, open ride search with the selected destination already applied. From the booking sheet, update the existing dropoff and route preview without disrupting the rest of the draft.

## Acceptance Criteria

- Ride service exposes an authenticated passenger route for recent destinations.
- Home recent rows no longer use `SDemoRides` static data.
- Booking sheet shows recent destinations between dropoff input and category strip.
- ETA is live from geospatial route calculation when an origin exists.
- Missing origin, empty history, and backend failures do not block booking.
- Tapping a recent destination updates the dropoff coordinates and text.
