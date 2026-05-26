# 056 Driver Requests Real-Time

Prompt summary:

Create the driver requests page in `client/lib/features/drivers/screens/requests` using real backend data. The page needs an online/offline app bar control, a list of nearby passenger ride requests, fixed and hybrid incoming ride bottom-sheet experiences, and an active-trip map state that suppresses new requests while a ride is assigned.

Backend requirements:

- Analyze and use Ride, Bidding, Location, Geospatial, and Verification service routes.
- Add missing Ride routes for driver request listing and active ride lookup.
- Use Geospatial routes for shortest route geometry instead of straight lines.
- Use Location service driver status and live GPS tracking.
- Use Bidding service for HYBRID ride offer submission.
- Follow existing clean architecture boundaries.

Client requirements:

- Follow existing driver/feature folder style.
- Keep one widget per widget file.
- Use real APIs, not demo data.
- Show active ride map with driver location, pickup/dropoff, route, and lifecycle buttons.
- Enable arrived-at-pickup only within a 20 meter pickup radius.

