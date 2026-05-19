import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/features/location/screens/ride_search/widgets/booking_sheet.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

void main() {
  testWidgets('booking sheet updates vehicle list when category changes',
      (tester) async {
    final controller = SRideSearchController();
    controller.pickup.value = const SAddressResult(
      formatted: 'Pickup',
      coordinate: SCoordinate(latitude: 31.52, longitude: 74.35),
    );
    controller.selectedDropoff.value = const SAddressResult(
      formatted: 'Dropoff',
      coordinate: SCoordinate(latitude: 31.60, longitude: 74.40),
    );
    controller.sheetMode.value = SBookingSheetMode.vehicles;

    await tester.pumpWidget(
      GetMaterialApp(
        home: Scaffold(
          body: SBookingSheet(controller: controller),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Moto'), findsOneWidget);

    await tester.tap(find.text('Freight'));
    await tester.pumpAndSettle();

    expect(find.text('Pickup'), findsOneWidget);
    expect(find.text('Moto'), findsNothing);
  });
}
