# Edit Destination & Cancel Ride (082)

## Prompt

Enable the passenger to edit the destination stop of their active ride and cancel the ride from the Ride Tracking Screen. 

## Requirements

### 1. Ride Cancellation
- Provide a clear cancellation action ("Cancel Ride") in the bottom details panel of [ride_tracking_screen.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/screens/ride_tracking/ride_tracking_screen.dart).
- Triggers a cancellation confirmation dialog with a selection of reasons.
- Calls `POST /rides/{ride_id}/cancel` through the repository to cancel the ride, broadcasts the updates, and returns the passenger to the home screen.

### 2. Destination Modification (Option A)
- Expose an interactive destination row in the Ride Tracking Screen bottom panel showing the current dropoff address with an edit button.
- Tapping "Edit" navigates to a new `RideDestinationEditScreen` matching the behavior of [booking_sheet.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/screens/ride_search/widgets/booking_sheet.dart):
  - Displays a map with a center pin selector.
  - Features an address search box with suggestions as the user types (using `SLocationRepository.searchPlaces`).
  - Confirms the map-pin coordinates via reverse geocoding (`SLocationRepository.reverseGeocode`).
- Clicking "Confirm" calls the backend API to update the destination stop coordinates.
- **Backend API Upgrade**: Add a `PATCH /stops/{stop_id}` route to update stop locations in database and trigger a WebSocket update to broadcast the updated stop location to the passenger and assigned driver.
- Redraws the new route on the passenger's and driver's maps immediately.
