import 'package:client/features/location/data/ride_repository.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
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

  test('builds backend hybrid passenger offer payload', () {
    final offer = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.cityRides,
    ).firstWhere((item) => item.id == 'city-mini');

    final body = SRideRepository.buildHybridRideRequest(
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
      offer: offer,
      passengerOffer: 250,
      autoAcceptDriver: true,
    );

    expect(body['service_type'], 'CITY_RIDE');
    expect(body['category'], 'MINI');
    expect(body['pricing_mode'], 'HYBRID');
    expect(body['baseline_min_price'], 213);
    expect(body['baseline_max_price'], 250);
    expect(body['auto_accept_driver'], isTrue);
    expect(body['detail']['preferred_vehicle_type'], 'HATCHBACK');
    expect(body['detail']['estimated_price'], 250);
  });

  test('builds backend freight detail with schema field names', () {
    final offer = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.freight,
    ).firstWhere((item) => item.id == 'freight-pickup');

    final body = SRideRepository.buildHybridRideRequest(
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
      offer: offer,
      passengerOffer: 1500,
      autoAcceptDriver: false,
    );

    expect(body['pricing_mode'], 'HYBRID');
    expect(body['detail']['cargo_weight'], 20);
    expect(body['detail'].containsKey('cargo_weight_kg'), isFalse);
  });

  test('builds backend courier detail with required recipient fields', () {
    final offer = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.courier,
    ).firstWhere((item) => item.id == 'courier-bike');

    final body = SRideRepository.buildHybridRideRequest(
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
      offer: offer,
      passengerOffer: 300,
      autoAcceptDriver: false,
    );

    expect(body['pricing_mode'], 'HYBRID');
    expect(body['detail']['item_weight'], 1);
    expect(body['detail']['recipient_name'], isNotEmpty);
    expect(body['detail']['recipient_phone'], isNotEmpty);
    expect(body['detail'].containsKey('item_weight_kg'), isFalse);
  });
}
