import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_details_content.dart';
import 'package:client/utils/theme/theme.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

void main() {
  testWidgets('city ride details controls repaint after interaction',
      (tester) async {
    final controller = SRideSearchController();
    controller.selectCategory(SPassengerServiceCategory.cityRides);
    controller.sheetMode.value = SBookingSheetMode.details;

    await tester.pumpWidget(
      GetMaterialApp(
        theme: SAppTheme.appTheme,
        home: Scaffold(
          body: SingleChildScrollView(
            child: SRideDetailsContent(controller: controller),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('1'), findsOneWidget);

    await tester.tap(
      find.descendant(
        of: find.ancestor(
          of: find.text('Passengers'),
          matching: find.byType(ListTile),
        ),
        matching: find.byIcon(Icons.add),
      ),
    );
    await tester.pump();

    expect(controller.cityPassengerCount.value, 2);
    expect(find.text('2'), findsOneWidget);

    final petSwitch = find.widgetWithText(SwitchListTile, 'Dog or pet allowed');
    expect(tester.widget<SwitchListTile>(petSwitch).value, isFalse);

    await tester.tap(petSwitch);
    await tester.pump();

    expect(controller.isPetAllowed.value, isTrue);
    expect(tester.widget<SwitchListTile>(petSwitch).value, isTrue);

    final hybridChip = find.widgetWithText(FilterChip, 'HYBRID');
    await tester.ensureVisible(hybridChip);
    await tester.pump();

    expect(tester.widget<FilterChip>(hybridChip).selected, isFalse);

    await tester.tap(hybridChip);
    await tester.pump();

    expect(controller.allowedFuelTypes, contains(SFuelType.hybrid));
    expect(tester.widget<FilterChip>(hybridChip).selected, isTrue);
  });

  testWidgets('intercity shared ride reveals co-passenger control',
      (tester) async {
    final controller = SRideSearchController();
    controller.selectCategory(SPassengerServiceCategory.cityToCity);
    controller.sheetMode.value = SBookingSheetMode.details;

    await tester.pumpWidget(
      GetMaterialApp(
        theme: SAppTheme.appTheme,
        home: Scaffold(
          body: SingleChildScrollView(
            child: SRideDetailsContent(controller: controller),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Max co-passengers'), findsNothing);

    await tester.tap(
      find.widgetWithText(SwitchListTile, 'Shared intercity ride'),
    );
    await tester.pump();

    expect(controller.isSharedIntercityRide.value, isTrue);
    expect(find.text('Max co-passengers'), findsOneWidget);
  });
}
