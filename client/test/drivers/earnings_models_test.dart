import 'package:client/features/drivers/domain/earnings_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('driver earnings response parses backend read model', () {
    final earnings = SDriverEarnings.fromJson({
      'period': 'today',
      'currency': 'PKR',
      'summary': {
        'net_earnings': 850.0,
        'gross_fares': 1000.0,
        'commission_total': 150.0,
        'available_balance': 1200.0,
        'reserved_balance': 0.0,
        'completed_trips': 1,
        'active_minutes': 22,
        'rating_avg': 4.8,
        'cash_collected': 1000.0,
        'platform_collected': 0.0,
      },
      'daily_breakdown': [
        {
          'label': 'Fri',
          'date': '2026-05-22',
          'gross_fares': 1000.0,
          'commission_total': 150.0,
          'net_earnings': 850.0,
          'completed_trips': 1,
        },
      ],
      'recent_trips': [
        {
          'ride_id': '22222222-2222-4222-8222-222222222222',
          'completed_at': '2026-05-22T12:30:00Z',
          'pickup_label': 'Gulberg',
          'dropoff_label': 'DHA Phase 5',
          'service_type': 'CITY_RIDE',
          'final_fare': 1000.0,
          'commission': 150.0,
          'net_earning': 850.0,
          'collection_mode': 'DRIVER_COLLECTED',
        },
      ],
      'withdraw_available': false,
      'withdraw_unavailable_reason': 'Withdrawals are not enabled yet.',
    });

    expect(earnings.currency, 'PKR');
    expect(earnings.summary.netEarnings, 850.0);
    expect(earnings.summary.completedTrips, 1);
    expect(earnings.dailyBreakdown.single.label, 'Fri');
    expect(earnings.recentTrips.single.netEarning, 850.0);
    expect(earnings.withdrawAvailable, isFalse);
  });
}
