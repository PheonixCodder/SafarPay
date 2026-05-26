# Passenger Ride UX And Trips Real Data

## Prompt

Improve the passenger-side ride experience where current screens still feel unfinished or use stale/demo data. Scope is limited to the ride creation details step, ride communication/call screens, and the Trips area.

## Requirements

- Replace fixed Trips data with rides fetched from the ride service using the authenticated passenger.
- Keep Trips divided into ongoing, scheduled, canceled, and completed states.
- Tapping an ongoing ride must open `RideTrackingScreen` with the ride id.
- Tapping completed/canceled/scheduled rides must open a details screen that refreshes full ride details from the backend.
- Redesign trip cards and empty/loading/error states so they look production-ready.
- Redesign the ride creation details step inside the booking bottom sheet into clear service, payment, fare, and review sections.
- Redesign communication and voice-call screens with a professional active-ride feel while preserving current chat, attachment, voice note, and WebRTC call behavior.
- Do not introduce unrelated backend changes; use the existing ride and communication APIs.

## Backend Contracts

- Passenger trip list: `GET /api/v1/rides`
- Full ride details: `GET /api/v1/rides/{ride_id}`
- Ongoing statuses: `CREATED`, `MATCHING`, `ACCEPTED`, `ARRIVING`, `IN_PROGRESS`
- Scheduled rides are non-terminal rides with `scheduled_at != null`.
- Communication is resolved by ride id through the communication service conversation lookup before chat and calls connect.

## Acceptance Criteria

- Trips no longer import or render `SDemoRides`.
- Trips screen refreshes from backend on load and pull-to-refresh.
- Ongoing trip cards route to live tracking without requiring stale full ride objects.
- Ride details fetch the latest ride state when opened.
- Communication and call screens retain all existing send/receive/call actions.
- Ride creation details step is visually grouped and easier to scan in a bottom sheet.
