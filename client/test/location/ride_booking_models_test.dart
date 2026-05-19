import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('city rides expose passenger vehicle choices for hybrid offers', () {
    final vehicles = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.cityRides,
    );

    expect(vehicles.map((item) => item.id), contains('city-moto'));
    expect(vehicles.map((item) => item.id), contains('city-mini'));
    expect(vehicles.map((item) => item.id), contains('city-rickshaw'));
    expect(vehicles.first.serviceType, ServiceType.cityRide);
  });

  test('grocery category is visible but gated until store selection exists', () {
    final service = SRideBookingCatalog.services.firstWhere(
      (item) => item.category == SPassengerServiceCategory.groceries,
    );
    final vehicles = SRideBookingCatalog.vehiclesFor(
      SPassengerServiceCategory.groceries,
    );

    expect(service.isBookable, isFalse);
    expect(vehicles.every((item) => item.isBookable == false), isTrue);
  });
}
