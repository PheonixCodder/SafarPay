import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/location/data/ride_repository.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('uses demo ride data when demo mode is enabled', () async {
    final repository = SRideRepository(useDemoData: true);

    final result = await repository.fetchRide('ride-123');

    expect(result['id'], 'ride-123');
  });

  test('parses passenger ride summaries from demo contract', () async {
    final repository = SRideRepository(useDemoData: true);

    final result = await repository.listPassengerRides();

    expect(result, isNotEmpty);
    expect(result.first.id, isNotEmpty);
    expect(result.first.pricingMode, PricingMode.hybrid);
    expect(result.first.pickupStop, isNotNull);
    expect(result.first.dropoffStop, isNotNull);
  });

  test('parses recent destinations from demo contract', () async {
    final repository = SRideRepository(useDemoData: true);

    final result = await repository.listRecentDestinations();

    expect(result, isNotEmpty);
    expect(result.first.rideId, isNotEmpty);
    expect(result.first.dropoffStop.stopType, StopType.dropoff);
    expect(result.first.dropoffStop.latitude, isNonZero);
  });

  test('parses legacy passenger ride summaries without pricing mode', () {
    final json = <String, dynamic>{
      'id': 'legacy-ride-001',
      'passenger_id': 'passenger-001',
      'assigned_driver_id': null,
      'service_type': 'CITY_RIDE',
      'category': 'MINI',
      'status': 'MATCHING',
      'passenger_payment_method': 'CASH',
      'payment_collection_mode': 'DRIVER_COLLECTED',
      'created_at': DateTime.now().toIso8601String(),
      'scheduled_at': null,
      'pickup_stop': null,
      'dropoff_stop': null,
    };

    final result = RideSummaryResponse.fromJson(json);

    expect(result.pricingMode, PricingMode.fixed);
  });

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
    expect(body['detail']['requires_otp_start'], isFalse);
    expect(body['detail']['requires_otp_end'], isFalse);
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
    expect(body['detail']['preferred_vehicle_type'], 'CAR');
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

  test('builds fixed city ride with passenger preferences', () {
    final offer = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.cityRides,
    ).firstWhere((item) => item.id == 'city-mini');

    final body = SRideRepository.buildRideRequest(
      draft: SRideBookingDraft(
        pickup: _pickup,
        dropoff: _dropoff,
        offer: offer,
        pricingMode: PricingMode.fixed,
        paymentMethod: PassengerPaymentMethod.jazzcash,
        city: const SCityRideOptions(
          passengerCount: 2,
          driverGenderPreference: SDriverGenderPreference.female,
          isPetAllowed: true,
          isSmokingAllowed: true,
          requiresWheelchairAccess: true,
          allowedFuelTypes: [SFuelType.hybrid],
          maxWaitTimeMinutes: 8,
        ),
      ),
    );

    expect(body['pricing_mode'], 'FIXED');
    expect(body.containsKey('baseline_min_price'), isFalse);
    expect(body['passenger_payment_method'], 'JAZZCASH');
    expect(body['detail']['is_shared_ride'], isFalse);
    expect(body['detail']['passenger_count'], 2);
    expect(body['detail']['driver_gender_preference'], 'FEMALE');
    expect(body['detail']['is_pet_allowed'], isTrue);
    expect(body['detail']['is_smoking_allowed'], isTrue);
    expect(body['detail']['requires_wheelchair_access'], isTrue);
    expect(body['detail']['allowed_fuel_types'], ['HYBRID']);
    expect(body['detail']['max_wait_time_minutes'], 8);
    expect(body['detail']['requires_otp_start'], isFalse);
    expect(body['detail']['requires_otp_end'], isFalse);
  });

  test('sends city ride OTP flags only when passenger enables them', () {
    final offer = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.cityRides,
    ).firstWhere((item) => item.id == 'city-mini');

    final body = SRideRepository.buildRideRequest(
      draft: SRideBookingDraft(
        pickup: _pickup,
        dropoff: _dropoff,
        offer: offer,
        city: const SCityRideOptions(
          requiresOtpStart: true,
          requiresOtpEnd: true,
        ),
      ),
    );

    expect(body['detail']['requires_otp_start'], isTrue);
    expect(body['detail']['requires_otp_end'], isTrue);
  });

  test('keeps shared ride options scoped to intercity rides', () {
    final cityOffer = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.cityRides,
    ).firstWhere((item) => item.id == 'city-mini');
    final intercityOffer = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.cityToCity,
    ).firstWhere((item) => item.id == 'intercity-car');

    final cityBody = SRideRepository.buildRideRequest(
      draft: SRideBookingDraft(
        pickup: _pickup,
        dropoff: _dropoff,
        offer: cityOffer,
        intercity: const SIntercityRideOptions(isSharedRide: true),
      ),
    );
    final intercityBody = SRideRepository.buildRideRequest(
      draft: SRideBookingDraft(
        pickup: _pickup,
        dropoff: _dropoff,
        offer: intercityOffer,
        intercity: const SIntercityRideOptions(
          passengerCount: 3,
          luggageCount: 2,
          isSharedRide: true,
          maxCoPassengers: 2,
        ),
      ),
    );

    expect(cityBody['detail']['is_shared_ride'], isFalse);
    expect(intercityBody['detail']['is_shared_ride'], isTrue);
    expect(intercityBody['detail']['max_co_passengers'], 2);
    expect(intercityBody['detail']['luggage_count'], 2);
  });

  test('builds courier and freight details from explicit options', () {
    final courierOffer = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.courier,
    ).firstWhere((item) => item.id == 'courier-bike');
    final freightOffer = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.freight,
    ).firstWhere((item) => item.id == 'freight-pickup');

    final courierBody = SRideRepository.buildRideRequest(
      draft: SRideBookingDraft(
        pickup: _pickup,
        dropoff: _dropoff,
        offer: courierOffer,
        courier: const SCourierRideOptions(
          itemDescription: 'Laptop bag',
          itemWeight: 3,
          totalParcels: 2,
          recipientName: 'Ali',
          recipientPhone: '03001234567',
          requiresSignature: true,
          isFragile: true,
          declaredValue: 50000,
        ),
      ),
    );
    final freightBody = SRideRepository.buildRideRequest(
      draft: SRideBookingDraft(
        pickup: _pickup,
        dropoff: _dropoff,
        offer: freightOffer,
        freight: const SFreightRideOptions(
          cargoWeight: 120,
          cargoType: 'Furniture',
          requiresLoader: true,
          isFragile: true,
          requiresTemperatureControl: true,
          declaredValue: 80000,
          commodityNotes: 'Glass table',
          estimatedLoadHours: 2,
        ),
      ),
    );

    expect(courierBody['detail']['item_description'], 'Laptop bag');
    expect(courierBody['detail']['recipient_name'], 'Ali');
    expect(courierBody['detail']['requires_signature'], isTrue);
    expect(freightBody['detail']['cargo_weight'], 120);
    expect(freightBody['detail']['cargo_type'], 'Furniture');
    expect(freightBody['detail']['requires_loader'], isTrue);
    expect(freightBody['detail']['requires_temperature_control'], isTrue);
  });
}

const _pickup = SAddressResult(
  formatted: 'Pickup address',
  coordinate: SCoordinate(latitude: 31.52, longitude: 74.35),
  city: 'Lahore',
  country: 'Pakistan',
);

const _dropoff = SAddressResult(
  formatted: 'Dropoff address',
  coordinate: SCoordinate(latitude: 31.60, longitude: 74.40),
  city: 'Lahore',
  country: 'Pakistan',
);
