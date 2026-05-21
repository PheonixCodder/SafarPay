# Driver Vehicle Service Reuse

## Prompt

When a driver selects a service category and then a vehicle type in driver registration, the app should use real verification backend state instead of demo data. If the driver already has that vehicle type registered for the selected service, the vehicle tile should show a circled tick instead of the arrow. If the driver already has the same physical vehicle type for another service, the app should reuse that vehicle and attach the selected service to it instead of creating a duplicate vehicle.

## Requirements

- Keep one vehicle per driver per physical vehicle type.
- Allow one vehicle to support multiple services through service capability rows.
- Reuse pending, rejected, or verified existing vehicles for new services.
- Scope verification status by selected service and vehicle type so the UI does not rely on whichever vehicle is currently selected.
- Remove verification demo fetching from the driver registration repository.

## Backend Contract

- `GET /api/v1/verification/driver/vehicles/summary?service_type=...` returns the driver's vehicles and service capabilities.
- `POST /api/v1/verification/driver/vehicles/{vehicle_id}/services` attaches an existing vehicle to a service.
- `GET /api/v1/verification/me` accepts optional `service_type` and `vehicle_type` filters.

## Client Flow

- Vehicle selection fetches the summary for the chosen service.
- Tiles show `tick_circle` when the vehicle is already registered for the selected service.
- Selecting a vehicle that exists for another service attaches that service, refreshes summary, and opens verification status.
- Selecting a new vehicle type opens the normal vehicle information flow from verification status.
