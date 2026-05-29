# Edit Destination & Cancel Ride Plan (082)

## Plan

1. **Backend Database & Repository Updates**:
   - In [interfaces.py](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/services/ride/ride/domain/interfaces.py), add `update_location(self, stop_id: UUID, latitude: float, longitude: float, place_name: str, address_line_1: str)` to the `StopRepositoryProtocol` contract.
   - In [repositories.py](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/services/ride/ride/infrastructure/repositories.py), implement the SQL update for stop location details in `StopRepository.update_location`.

2. **Backend UseCase & Routing (Option A)**:
   - Create `UpdateStopRequest` schema in [schemas.py](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/services/ride/ride/application/schemas.py) for the input fields.
   - Implement `UpdateStopUseCase` in [use_cases.py](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/services/ride/ride/application/use_cases.py) to authorize that the requesting passenger owns the ride, update the stop coordinates/address in DB, and broadcast a `STOP_UPDATED` event to the driver and passenger.
   - Expose the `PATCH /stops/{stop_id}` endpoint in [router.py](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/services/ride/ride/api/router.py).

3. **Client Repository**:
   - Add `updateStop` method to [SRideRepository](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/data/ride_repository.dart):
     - The HTTP delegate performs a `PATCH` request to `/stops/{stop_id}`.
     - The Demo delegate updates local mock data in memory.

4. **Client Controller**:
   - In [ride_tracking_controller.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/controllers/ride_tracking_controller.dart):
     - Add `cancelCurrentRide(String reason)` to call `_rideRepository.cancelRide` and navigate back to the home screen.
     - Add `updateRideDestination(SAddressResult newDestination)` to call `updateStop` with the dropoff stop ID.
     - Ensure the websocket listener refreshes the route and map markers automatically when a `STOP_UPDATED` event is received.

5. **Client UI - Edit Destination Screen**:
   - Create `RideDestinationEditScreen` mimicking the map and search behaviors of [booking_sheet.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/screens/ride_search/widgets/booking_sheet.dart):
     - Interactive text input for address search.
     - Full screen map panning with a center pin selector.
     - Floating GPS/Recenter check button (`confirmMapPin`) that does reverse geocoding to retrieve the address.
     - A confirmation CTA button that triggers the controller's `updateRideDestination`.

6. **Client UI - Ride Details Panel**:
   - Update [ride_tracking_screen.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/screens/ride_tracking/ride_tracking_screen.dart) to show:
     - The active dropoff address in the bottom panel with an "Edit" icon.
     - A clean red "Cancel Ride" button.
     - Confirmation dialogs for both actions.
