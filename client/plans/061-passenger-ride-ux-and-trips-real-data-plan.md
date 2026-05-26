# Passenger Ride UX And Trips Real Data Plan

## Implementation Plan

1. Add typed passenger ride summary support in the client ride model and repository.
2. Add a Trips controller that loads real passenger rides, filters tabs, exposes loading/error/refresh state, and keeps tab selection out of the view.
3. Replace Trips static tab screens with controller-backed list views and redesigned cards.
4. Update ride details navigation to pass a ride id, fetch fresh details, and show loading/error states.
5. Redesign the booking details step with dedicated section widgets while keeping the current service-option and pricing controls.
6. Refresh communication/chat UI and call UI without changing existing controller behavior or API contracts.
7. Add focused model/controller tests where feasible and run Flutter analysis for the touched client surfaces.

## Notes

- Keep the scope to named passenger surfaces only.
- Preserve existing route/service URLs and auth behavior.
- Avoid broad visual rewrites of home/profile/driver requests/earnings because those screens are already accepted.
