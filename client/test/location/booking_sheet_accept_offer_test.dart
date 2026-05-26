import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/data/bidding_repository.dart';
import 'package:client/features/location/domain/bidding_models.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/features/location/screens/ride_search/widgets/booking_sheet.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

void main() {
  testWidgets('accepted demo offer requests ride tracking navigation',
      (tester) async {
    final controller = SRideSearchController(
      biddingRepository: const SBiddingRepository(useDemoData: true),
    );
    controller.sheetMode.value = SBookingSheetMode.matching;
    controller.createdRideId.value = 'demo-ride-001';
    controller.biddingSessionId.value = 'demo-hybrid-session-001';
    controller.driverBids.add(
      SBid.fromJson({
        'id': 'demo-driver-bid-001',
        'bidding_session_id': 'demo-hybrid-session-001',
        'driver_id': 'demo-driver-001',
        'driver_vehicle_id': null,
        'bid_amount': 245,
        'currency': 'PKR',
        'eta_minutes': 4,
        'message': 'Demo live offer',
        'status': 'PLACED',
        'placed_at': '2026-05-18T12:00:00Z',
      }),
    );

    final requestedRideIds = <String>[];

    await tester.pumpWidget(
      GetMaterialApp(
        home: Scaffold(
          body: SBookingSheet(
            controller: controller,
            onAcceptedRideTrackingRequested: requestedRideIds.add,
          ),
        ),
      ),
    );
    await tester.pump();

    await tester.tap(find.text('Accept'));
    await tester.pump(const Duration(milliseconds: 100));

    expect(requestedRideIds, ['demo-ride-001']);
  });
}
