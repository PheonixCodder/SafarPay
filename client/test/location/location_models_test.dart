import 'package:client/features/location/domain/location_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SCoordinate', () {
    test('parses backend latitude and longitude fields', () {
      final coordinate = SCoordinate.fromJson({
        'latitude': 31.5204,
        'longitude': 74.3587,
      });

      expect(coordinate.latitude, 31.5204);
      expect(coordinate.longitude, 74.3587);
      expect(coordinate.toJson(), {
        'latitude': 31.5204,
        'longitude': 74.3587,
      });
    });

    test('parses client lat and lng aliases', () {
      final coordinate = SCoordinate.fromJson({
        'lat': 31.5204,
        'lng': 74.3587,
      });

      expect(coordinate.latitude, 31.5204);
      expect(coordinate.longitude, 74.3587);
    });
  });

  group('SAddressResult', () {
    test('parses location service geocode response', () {
      final result = SAddressResult.fromJson({
        'formatted': 'Model Town, Lahore, Pakistan',
        'street': 'Model Town',
        'city': 'Lahore',
        'country': 'Pakistan',
        'postal_code': '54700',
        'coordinates': {
          'latitude': 31.4801,
          'longitude': 74.3239,
        },
      });

      expect(result.formatted, 'Model Town, Lahore, Pakistan');
      expect(result.displayLabel, 'Model Town, Lahore, Pakistan');
      expect(result.city, 'Lahore');
      expect(result.coordinate.latitude, 31.4801);
      expect(result.coordinate.longitude, 74.3239);
    });

    test('displayLabel hides coordinate-only formatted text', () {
      const result = SAddressResult(
        formatted: '31.53723, 74.42631',
        coordinate: SCoordinate(latitude: 31.53723, longitude: 74.42631),
        street: 'Main Boulevard',
        city: 'Lahore',
        country: 'Pakistan',
      );

      expect(result.isCoordinateLikeFormatted, isTrue);
      expect(result.displayLabel, 'Main Boulevard, Lahore, Pakistan');
    });

    test('tryParseCoordinateQuery parses lat lng pairs', () {
      final coordinate =
          SAddressResult.tryParseCoordinateQuery('31.53723, 74.42631');

      expect(coordinate?.latitude, 31.53723);
      expect(coordinate?.longitude, 74.42631);
      expect(SAddressResult.isCoordinateLikeQuery('Gulberg'), isFalse);
    });
  });

  group('SRoutePreview', () {
    test('parses geospatial route response with steps', () {
      final route = SRoutePreview.fromJson({
        'distance_km': 8.5,
        'duration_minutes': 22.0,
        'polyline': 'encoded_route',
        'steps': [
          {
            'instruction': 'Head north',
            'distance_meters': 200.0,
            'duration_seconds': 40.0,
            'polyline': 'step_polyline',
          }
        ],
      });

      expect(route.distanceKm, 8.5);
      expect(route.durationMinutes, 22.0);
      expect(route.polyline, 'encoded_route');
      expect(route.steps.single.instruction, 'Head north');
    });
  });

  group('SLiveRideLocations', () {
    test('parses live ride location response when driver is present', () {
      final locations = SLiveRideLocations.fromJson({
        'ride_id': 'ride-1',
        'driver': {
          'driver_id': 'driver-1',
          'lat': 31.52,
          'lng': 74.35,
          'heading': 180.0,
          'speed': 42.0,
          'updated_at': '2026-05-17T12:00:00Z',
        },
        'passenger': {
          'user_id': 'user-1',
          'lat': 31.50,
          'lng': 74.30,
          'updated_at': '2026-05-17T12:00:01Z',
        },
      });

      expect(locations.rideId, 'ride-1');
      expect(locations.driver?.driverId, 'driver-1');
      expect(locations.driver?.coordinate.longitude, 74.35);
      expect(locations.passenger?.userId, 'user-1');
    });
  });
}
