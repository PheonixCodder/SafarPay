import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('ride search controller starts with provided initial category', () async {
    final controller = SRideSearchController(
      initialCategory: SPassengerServiceCategory.freight,
    );

    controller.onInit();
    await Future<void>.delayed(const Duration(milliseconds: 20));

    expect(controller.selectedCategory.value, SPassengerServiceCategory.freight);
    expect(controller.selectedVehicle.value?.id, 'freight-pickup');
    expect(
      controller.availableVehicles.map((vehicle) => vehicle.id),
      contains('freight-mini-truck'),
    );

    controller.onClose();
  });
}
