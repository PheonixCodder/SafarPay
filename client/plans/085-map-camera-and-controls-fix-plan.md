# Map Camera & Controls Fix Plan (085)

## Plan

1. **Add `flyToCoordinate` to `SMapController`**:
   - In [map_models.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/common/widgets/maps/map_models.dart), add a `FlyToCallback` typedef and a `flyToCoordinate(SCoordinate)` method to `SMapController`.
   - In [map_view.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/common/widgets/maps/map_view.dart), attach the fly-to callback in `_handleMapCreated` alongside the existing `attachCameraReader`. The callback calls `_moveCamera(CameraOptions(...), animated: true)`.

2. **Fix Initial Camera Position**:
   - In [ride_search_controller.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/controllers/ride_search_controller.dart), inside `loadCurrentPickup()`:
     - After getting the device coordinate from `_deviceLocationService.currentCoordinate()` and **before** the async `reverseGeocode` call, immediately fly the map to the device coordinate via `mapController.flyToCoordinate(coordinate)`.
     - This ensures the map moves to the user's GPS position instantly, without waiting for the reverse geocode round-trip.

3. **Add `goToMyLocation` Method to Controller**:
   - In [ride_search_controller.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/controllers/ride_search_controller.dart), add:
     ```dart
     final RxBool isLocating = false.obs;
     
     Future<void> goToMyLocation() async {
       isLocating.value = true;
       try {
         final coordinate = await _deviceLocationService.currentCoordinate();
         _hasDeviceLocation = true;
         mapController.flyToCoordinate(coordinate);
       } catch (_) {
         errorMessage.value = 'Unable to get your location.';
       } finally {
         isLocating.value = false;
       }
     }
     ```

4. **Redesign `SBookingMapControls` Layout**:
   - In [booking_map_controls.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/screens/ride_search/widgets/booking_map_controls.dart):
     - Keep the back button at top-left inside a `SafeArea` + `Padding`.
     - Move the action buttons (pin-confirm + new my-location) to a `Positioned` widget on the right side, vertically above the bottom sheet (~`bottom: 380, right: 16`).
     - Stack them in a `Column` with `SSizes.sm` gap:
       - **Pin-confirm button** (Iconsax.gps icon, calls `controller.confirmMapPin`) — existing behavior.
       - **My Location button** (Icons.my_location icon, calls `controller.goToMyLocation`) — new.
     - Both use the existing `_MapButton` widget.

5. **Update `ride_search_screen.dart`**:
   - In [ride_search_screen.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/screens/ride_search/ride_search_screen.dart), ensure the `SBookingMapControls` `Positioned` widget allows room for the right-side buttons by removing `top: 0` constraint if needed, or by splitting into two `Positioned` zones (top-left for back, right-side for action buttons).
