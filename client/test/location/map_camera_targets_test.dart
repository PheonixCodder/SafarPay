import 'package:client/common/widgets/maps/map_camera_targets.dart';
import 'package:client/common/widgets/maps/map_models.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SMapCameraTargets', () {
    const driver = SMapMarker(
      id: 'driver',
      coordinate: SCoordinate(latitude: 31.5204, longitude: 74.3587),
      type: SMapMarkerType.driver,
      label: 'Driver',
    );
    const pickup = SMapMarker(
      id: 'pickup',
      coordinate: SCoordinate(latitude: 31.5250, longitude: 74.3700),
      type: SMapMarkerType.pickup,
      label: 'Pickup',
    );
    const route = SRoutePreview(
      distanceKm: 1,
      durationMinutes: 2,
      polyline: '_p~iF~ps|U_ulLnnqC_mqNvxq`@',
      steps: [],
    );

    test('navigation follow tracks driver instead of fitting route', () {
      final coordinates = SMapCameraTargets.coordinates(
        mode: SMapCameraMode.navigationFollow,
        route: route,
        markers: const [driver, pickup],
      );

      expect(coordinates, hasLength(1));
      expect(coordinates.single, driver.coordinate);
    });

    test('fit route still uses decoded route coordinates', () {
      final coordinates = SMapCameraTargets.coordinates(
        mode: SMapCameraMode.fitRoute,
        route: route,
        markers: const [driver, pickup],
      );

      expect(coordinates, hasLength(3));
      expect(coordinates.first.latitude, closeTo(38.5, 0.00001));
    });
  });
}
