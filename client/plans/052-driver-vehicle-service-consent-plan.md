# Driver Vehicle Service Consent Plan

## Summary

Add a frontend confirmation step before reusing an existing driver vehicle for a newly selected service. The backend reuse model stays unchanged: one physical vehicle per vehicle type can support many services through service capability rows.

## Implementation

- Update vehicle selection tap handling so service attachment is never automatic.
- Show a confirmation dialog when the selected vehicle exists but is not registered for the chosen service.
- Confirming calls the existing attach-service repository method, reloads summary, and opens verification status.
- Canceling closes the dialog and leaves the driver on vehicle selection without backend changes.
- Add text constants for the dialog title, body template, cancel, and confirm actions.

## Tests

- Tap a new vehicle type: no dialog; verification status opens.
- Tap a vehicle already registered for the selected service: no dialog; verification status opens.
- Tap an existing vehicle for a new service and cancel: no attach call and no navigation.
- Tap an existing vehicle for a new service and confirm: attach call succeeds, summary refreshes, and verification status opens.
- Run `flutter analyze` from `client/` and report unrelated existing analyzer issues separately.

## Notes

- This is a client consent change only.
- `driver_service_capabilities` remains the backend source of service membership.
- Existing vehicle verification is reused; drivers do not re-upload vehicle documents just to use the same vehicle for another service.
