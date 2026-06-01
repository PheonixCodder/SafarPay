# Map Camera & Controls Fix (085)

## Prompt

Fix three issues with the ride search map: (1) the map always opens at a hardcoded Lahore fallback instead of the user's current GPS position, (2) the map control buttons are misaligned (only a back button and a pin-confirm button in a flat row at the top), and (3) there is no "go to my current location" button.

## Requirements

### 1. Map Should Center on User's GPS Position on Load
- When the ride search screen opens, the map must center on the user's real device GPS position — not the static `fallbackCenter` (Lahore 31.52, 74.35).
- Root cause: `SMapView.initialCenter` is set to `mapCenter` which returns `fallbackCenter` because `pickup.value` is still `null` when the widget first builds (the async `loadCurrentPickup()` hasn't completed yet). The `cameraMode` is `manual`, so `_syncCamera` returns early without moving the camera later.
- The map should fly to the user's GPS position once `loadCurrentPickup()` resolves the device coordinate, even before the reverse geocode completes.

### 2. Fix Map Control Button Layout
- Currently [booking_map_controls.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/location/screens/ride_search/widgets/booking_map_controls.dart) places a back button (left) and a GPS pin-confirm button (right) in a horizontal `Row` at the top of the screen.
- Relocate the action buttons (pin-confirm and new recenter button) to a vertical `Column` on the right side of the screen, above the bottom sheet. The back button remains at the top-left.

### 3. Add "Go to My Location" Button
- Add a third map control button with a `my_location` (or `Iconsax.gps_slash` → `Iconsax.gps`) icon that flies the map camera to the user's current device GPS position.
- This calls `_deviceLocationService.currentCoordinate()` and then `mapController` to fly the camera there.
- Place this button below the existing pin-confirm button in the right-side vertical column.
