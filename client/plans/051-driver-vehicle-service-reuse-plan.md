# Driver Vehicle Service Reuse Plan

## Summary

Implement real backend-backed driver vehicle selection so a driver can reuse one physical vehicle across multiple services without creating duplicate vehicles.

## Implementation

- Add verification schemas and use cases for vehicle summary and attaching a service to an existing vehicle.
- Add verification routes for summary and attach-service behavior.
- Keep `POST /driver/vehicle` focused on creating/updating vehicle details and document upload URLs.
- Scope `GET /me` by optional `service_type` and `vehicle_type`.
- Add client models for vehicle summary and service capability responses.
- Remove demo fetching from `SDriverVerificationRepository`.
- Add a vehicle selection controller that loads summary, checks tile state, and attaches existing vehicles when needed.
- Extend the shared driver registration option tile with a completed tick state.

## Tests

- Backend compile check for changed verification modules.
- Verification unit and route tests for summary and attach-service behavior.
- Flutter driver registration model/controller tests for summary parsing and status behavior.

## Notes

- Existing pending/rejected vehicles are reused for new services.
- `driver_service_capabilities` remains the source of service membership.
- Existing environment blocks verification pytest collection until `cv2` is installed.
