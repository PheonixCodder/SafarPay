enum SDriverEarningsPeriod {
  today('today', 'Today'),
  week('week', 'Week'),
  month('month', 'Month');

  const SDriverEarningsPeriod(this.value, this.label);

  final String value;
  final String label;
}

class SDriverEarnings {
  const SDriverEarnings({
    required this.period,
    required this.currency,
    required this.summary,
    required this.dailyBreakdown,
    required this.recentTrips,
    required this.withdrawAvailable,
    this.withdrawUnavailableReason,
  });

  final String period;
  final String currency;
  final SDriverEarningsSummary summary;
  final List<SDriverEarningsBreakdownItem> dailyBreakdown;
  final List<SDriverEarningsTrip> recentTrips;
  final bool withdrawAvailable;
  final String? withdrawUnavailableReason;

  factory SDriverEarnings.fromJson(Map<String, dynamic> json) {
    return SDriverEarnings(
      period: _asString(json['period'], fallback: 'today'),
      currency: _asString(json['currency'], fallback: 'PKR'),
      summary: SDriverEarningsSummary.fromJson(
        _asMap(json['summary']),
      ),
      dailyBreakdown: _asList(json['daily_breakdown'])
          .map(SDriverEarningsBreakdownItem.fromJson)
          .toList(),
      recentTrips: _asList(json['recent_trips'])
          .map(SDriverEarningsTrip.fromJson)
          .toList(),
      withdrawAvailable: json['withdraw_available'] == true,
      withdrawUnavailableReason: json['withdraw_unavailable_reason']?.toString(),
    );
  }
}

class SDriverEarningsSummary {
  const SDriverEarningsSummary({
    required this.netEarnings,
    required this.grossFares,
    required this.commissionTotal,
    required this.availableBalance,
    required this.reservedBalance,
    required this.completedTrips,
    required this.activeMinutes,
    required this.ratingAvg,
    required this.cashCollected,
    required this.platformCollected,
  });

  final double netEarnings;
  final double grossFares;
  final double commissionTotal;
  final double availableBalance;
  final double reservedBalance;
  final int completedTrips;
  final int activeMinutes;
  final double? ratingAvg;
  final double cashCollected;
  final double platformCollected;

  factory SDriverEarningsSummary.fromJson(Map<String, dynamic> json) {
    return SDriverEarningsSummary(
      netEarnings: _asDouble(json['net_earnings']),
      grossFares: _asDouble(json['gross_fares']),
      commissionTotal: _asDouble(json['commission_total']),
      availableBalance: _asDouble(json['available_balance']),
      reservedBalance: _asDouble(json['reserved_balance']),
      completedTrips: _asInt(json['completed_trips']),
      activeMinutes: _asInt(json['active_minutes']),
      ratingAvg: json['rating_avg'] == null ? null : _asDouble(json['rating_avg']),
      cashCollected: _asDouble(json['cash_collected']),
      platformCollected: _asDouble(json['platform_collected']),
    );
  }
}

class SDriverEarningsBreakdownItem {
  const SDriverEarningsBreakdownItem({
    required this.label,
    required this.date,
    required this.grossFares,
    required this.commissionTotal,
    required this.netEarnings,
    required this.completedTrips,
  });

  final String label;
  final String date;
  final double grossFares;
  final double commissionTotal;
  final double netEarnings;
  final int completedTrips;

  factory SDriverEarningsBreakdownItem.fromJson(Map<String, dynamic> json) {
    return SDriverEarningsBreakdownItem(
      label: _asString(json['label']),
      date: _asString(json['date']),
      grossFares: _asDouble(json['gross_fares']),
      commissionTotal: _asDouble(json['commission_total']),
      netEarnings: _asDouble(json['net_earnings']),
      completedTrips: _asInt(json['completed_trips']),
    );
  }
}

class SDriverEarningsTrip {
  const SDriverEarningsTrip({
    required this.rideId,
    required this.completedAt,
    required this.pickupLabel,
    required this.dropoffLabel,
    required this.serviceType,
    required this.finalFare,
    required this.commission,
    required this.netEarning,
    required this.collectionMode,
  });

  final String rideId;
  final DateTime completedAt;
  final String pickupLabel;
  final String dropoffLabel;
  final String serviceType;
  final double finalFare;
  final double commission;
  final double netEarning;
  final String collectionMode;

  factory SDriverEarningsTrip.fromJson(Map<String, dynamic> json) {
    return SDriverEarningsTrip(
      rideId: _asString(json['ride_id']),
      completedAt: DateTime.tryParse(_asString(json['completed_at'])) ??
          DateTime.fromMillisecondsSinceEpoch(0),
      pickupLabel: _asString(json['pickup_label'], fallback: 'Pickup'),
      dropoffLabel: _asString(json['dropoff_label'], fallback: 'Dropoff'),
      serviceType: _asString(json['service_type'], fallback: 'CITY_RIDE'),
      finalFare: _asDouble(json['final_fare']),
      commission: _asDouble(json['commission']),
      netEarning: _asDouble(json['net_earning']),
      collectionMode:
          _asString(json['collection_mode'], fallback: 'DRIVER_COLLECTED'),
    );
  }
}

double _asDouble(dynamic value) {
  if (value is num) return value.toDouble();
  return double.tryParse(value?.toString() ?? '') ?? 0;
}

int _asInt(dynamic value) {
  if (value is int) return value;
  if (value is num) return value.toInt();
  return int.tryParse(value?.toString() ?? '') ?? 0;
}

String _asString(dynamic value, {String fallback = ''}) {
  final text = value?.toString();
  if (text == null || text.isEmpty) return fallback;
  return text;
}

Map<String, dynamic> _asMap(dynamic value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) return Map<String, dynamic>.from(value);
  return const {};
}

List<Map<String, dynamic>> _asList(dynamic value) {
  if (value is! List) return const [];
  return value
      .whereType<Map>()
      .map((item) => Map<String, dynamic>.from(item))
      .toList();
}
