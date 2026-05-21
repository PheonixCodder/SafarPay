# Driver Vehicle Service Consent

## Prompt

When a driver chooses a service category and taps a vehicle type that already exists on their account but is not yet registered for that selected service, the app must ask for explicit confirmation before attaching the existing vehicle to the new service.

## Requirements

- Keep the one-vehicle-per-driver-per-vehicle-type rule.
- Continue reusing a physical vehicle across multiple services through service capability rows.
- Do not silently attach an existing vehicle to a new service on tap.
- Show a confirmation popup only when the vehicle exists and is not already registered for the selected service.
- If the driver cancels, stay on vehicle selection and do not call the attach-service endpoint.
- If the driver confirms, call the existing attach-service endpoint, refresh summary, and navigate to verification status.
- Do not change backend contracts, routes, tables, or verification rules.

## Client Flow

- `driver_registration.dart` opens vehicle selection for the chosen service category.
- `vehicle_selection_screen.dart` loads the real vehicle summary for that service.
- Tapping a new vehicle type opens the normal verification status flow.
- Tapping a vehicle already registered for that service opens verification status directly.
- Tapping an existing vehicle that belongs to another service shows the consent dialog before attaching it to the selected service.

## Backend Contract

- Keep using `GET /api/v1/verification/driver/vehicles/summary?service_type=...`.
- Keep using `POST /api/v1/verification/driver/vehicles/{vehicle_id}/services`.
- No backend behavior changes are required for this consent step.
