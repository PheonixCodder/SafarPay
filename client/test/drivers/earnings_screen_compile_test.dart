import 'package:client/features/drivers/controllers/earnings_controller.dart';
import 'package:client/features/drivers/data/driver_earnings_repository.dart';
import 'package:client/features/drivers/domain/earnings_models.dart';
import 'package:client/features/drivers/screens/earnings/earnings.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:get/get.dart';

class _FakeEarningsRepository implements SDriverEarningsRepository {
  @override
  Future<SDriverEarnings> fetchEarnings(SDriverEarningsPeriod period) async {
    return SDriverEarnings(
      period: period.value,
      currency: 'PKR',
      summary: const SDriverEarningsSummary(
        netEarnings: 850,
        grossFares: 1000,
        commissionTotal: 150,
        availableBalance: 1200,
        reservedBalance: 0,
        completedTrips: 1,
        activeMinutes: 22,
        ratingAvg: 4.8,
        cashCollected: 1000,
        platformCollected: 0,
      ),
      dailyBreakdown: const [
        SDriverEarningsBreakdownItem(
          label: 'Fri',
          date: '2026-05-22',
          grossFares: 1000,
          commissionTotal: 150,
          netEarnings: 850,
          completedTrips: 1,
        ),
      ],
      recentTrips: [
        SDriverEarningsTrip(
          rideId: '22222222-2222-4222-8222-222222222222',
          completedAt: DateTime.utc(2026, 5, 22, 12, 30),
          pickupLabel: 'Gulberg',
          dropoffLabel: 'DHA Phase 5',
          serviceType: 'CITY_RIDE',
          finalFare: 1000,
          commission: 150,
          netEarning: 850,
          collectionMode: 'DRIVER_COLLECTED',
        ),
      ],
      withdrawAvailable: false,
      withdrawUnavailableReason: 'Withdrawals are not enabled yet.',
    );
  }
}

void main() {
  tearDown(Get.reset);

  testWidgets('earnings screen renders backend-backed dashboard sections',
      (tester) async {
    final controller = SEarningsController(
      repository: _FakeEarningsRepository(),
    );

    await tester.pumpWidget(
      GetMaterialApp(
        home: SEarningsScreen(controller: controller),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text(STexts.earningsTitle), findsOneWidget);
    expect(find.text(STexts.earningsOverview), findsOneWidget);
    await tester.drag(find.byType(ListView), const Offset(0, -420));
    await tester.pumpAndSettle();
    expect(find.text(STexts.earningsBreakdown), findsOneWidget);
    await tester.drag(find.byType(ListView), const Offset(0, -420));
    await tester.pumpAndSettle();
    expect(find.text(STexts.earningsRecentTrips), findsOneWidget);
  });
}
