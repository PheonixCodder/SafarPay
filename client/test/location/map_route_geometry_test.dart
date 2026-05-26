import 'package:client/common/widgets/maps/map_route_geometry.dart';
import 'package:client/features/location/data/demo/location_demo_data.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SMapRouteGeometry', () {
    test('decodes encoded route polylines into coordinates', () {
      final coordinates = SMapRouteGeometry.coordinatesForRoute(
        route: const SRoutePreview(
          distanceKm: 1,
          durationMinutes: 2,
          polyline: '_p~iF~ps|U_ulLnnqC_mqNvxq`@',
          steps: [],
        ),
        markers: const [],
      );

      expect(coordinates, hasLength(3));
      expect(coordinates[0].latitude, closeTo(38.5, 0.00001));
      expect(coordinates[0].longitude, closeTo(-120.2, 0.00001));
      expect(coordinates[2].latitude, closeTo(43.252, 0.00001));
      expect(coordinates[2].longitude, closeTo(-126.453, 0.00001));
    });

    test('does not draw a straight line when route geometry is missing', () {
      final coordinates = SMapRouteGeometry.coordinatesForRoute(
        route: null,
        markers: const [
          SMapRoutePoint(
            id: 'pickup',
            coordinate: SCoordinate(latitude: 31.5204, longitude: 74.3587),
            isPickup: true,
          ),
          SMapRoutePoint(
            id: 'dropoff',
            coordinate: SCoordinate(latitude: 31.4700, longitude: 74.4100),
            isPickup: false,
          ),
        ],
      );

      expect(coordinates, isEmpty);
    });

    test('does not draw a straight line when route geometry is invalid', () {
      final coordinates = SMapRouteGeometry.coordinatesForRoute(
        route: const SRoutePreview(
          distanceKm: 1,
          durationMinutes: 2,
          polyline: 'mock_polyline',
          steps: [],
        ),
        markers: const [
          SMapRoutePoint(
            id: 'pickup',
            coordinate: SCoordinate(latitude: 31.5204, longitude: 74.3587),
            isPickup: true,
          ),
          SMapRoutePoint(
            id: 'dropoff',
            coordinate: SCoordinate(latitude: 31.4700, longitude: 74.4100),
            isPickup: false,
          ),
        ],
      );

      expect(coordinates, isEmpty);
    });

    test('demo route provides decodable route geometry', () {
      final coordinates = SMapRouteGeometry.coordinatesForRoute(
        route: SLocationDemoData.routePreview,
        markers: const [],
      );

      expect(coordinates.length, greaterThanOrEqualTo(2));
      expect(coordinates.first.latitude, closeTo(31.4821, 0.00001));
      expect(coordinates.last.longitude, closeTo(74.4018, 0.00001));
    });

    test('returns no route coordinates until both ends exist', () {
      final coordinates = SMapRouteGeometry.coordinatesForRoute(
        route: null,
        markers: const [
          SMapRoutePoint(
            id: 'pickup',
            coordinate: SCoordinate(latitude: 31.5204, longitude: 74.3587),
            isPickup: true,
          ),
        ],
      );

      expect(coordinates, isEmpty);
    });
  });
}
