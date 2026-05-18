import 'package:client/features/location/data/ride_repository.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('builds backend city ride create payload', () {
    final body = SRideRepository.buildCityRideRequest(
      pickup: const SAddressResult(
        formatted: 'Pickup address',
        coordinate: SCoordinate(latitude: 31.52, longitude: 74.35),
        city: 'Lahore',
        country: 'Pakistan',
      ),
      dropoff: const SAddressResult(
        formatted: 'Dropoff address',
        coordinate: SCoordinate(latitude: 31.60, longitude: 74.40),
        city: 'Lahore',
        country: 'Pakistan',
      ),
    );

    expect(body['service_type'], 'CITY_RIDE');
    expect(body['category'], 'MINI');
    expect(body['pricing_mode'], 'FIXED');
    expect(body['passenger_payment_method'], 'CASH');
    expect(body['stops'], hasLength(2));
    expect(body['stops'][0]['stop_type'], 'PICKUP');
    expect(body['stops'][1]['stop_type'], 'DROPOFF');
    expect(body['detail']['service_type'], 'CITY_RIDE');
  });
}
