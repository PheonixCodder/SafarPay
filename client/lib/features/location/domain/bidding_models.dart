import '../../../data/rides/ride_models.dart';

class SBid {
  const SBid({
    required this.id,
    required this.biddingSessionId,
    required this.driverId,
    required this.driverVehicleId,
    required this.bidAmount,
    required this.currency,
    required this.etaMinutes,
    required this.message,
    required this.status,
    required this.placedAt,
  });

  final String id;
  final String biddingSessionId;
  final String driverId;
  final String? driverVehicleId;
  final double bidAmount;
  final String currency;
  final int? etaMinutes;
  final String? message;
  final String status;
  final DateTime placedAt;

  factory SBid.fromJson(Map<String, dynamic> json) {
    return SBid(
      id: json['id'] as String,
      biddingSessionId: json['bidding_session_id'] as String,
      driverId: json['driver_id'] as String,
      driverVehicleId: json['driver_vehicle_id'] as String?,
      bidAmount: _toDouble(json['bid_amount']) ?? 0,
      currency: json['currency']?.toString() ?? 'PKR',
      etaMinutes: _toInt(json['eta_minutes']),
      message: json['message'] as String?,
      status: json['status']?.toString() ?? '',
      placedAt: DateTime.parse(json['placed_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'bidding_session_id': biddingSessionId,
      'driver_id': driverId,
      'driver_vehicle_id': driverVehicleId,
      'bid_amount': bidAmount,
      'currency': currency,
      'eta_minutes': etaMinutes,
      'message': message,
      'status': status,
      'placed_at': placedAt.toIso8601String(),
    };
  }
}

class SCounterOffer {
  const SCounterOffer({
    required this.id,
    required this.sessionId,
    required this.price,
    required this.etaMinutes,
    required this.userId,
    required this.driverId,
    required this.bidId,
    required this.status,
    required this.respondedAt,
    required this.reason,
    required this.createdAt,
  });

  final String id;
  final String sessionId;
  final double price;
  final int? etaMinutes;
  final String? userId;
  final String? driverId;
  final String? bidId;
  final String status;
  final DateTime? respondedAt;
  final String? reason;
  final DateTime createdAt;

  factory SCounterOffer.fromJson(
    Map<String, dynamic> json, {
    String? fallbackSessionId,
  }) {
    return SCounterOffer(
      id: json['id'] as String,
      sessionId: json['session_id']?.toString() ?? fallbackSessionId ?? '',
      price: _toDouble(json['price']) ?? 0,
      etaMinutes: _toInt(json['eta_minutes']),
      userId: json['user_id'] as String?,
      driverId: json['driver_id'] as String?,
      bidId: json['bid_id'] as String?,
      status: json['status']?.toString() ?? '',
      respondedAt: _toDateTime(json['responded_at']),
      reason: json['reason'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'session_id': sessionId,
      'price': price,
      'eta_minutes': etaMinutes,
      'user_id': userId,
      'driver_id': driverId,
      'bid_id': bidId,
      'status': status,
      'responded_at': respondedAt?.toIso8601String(),
      'reason': reason,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

class SBiddingSession {
  const SBiddingSession({
    required this.sessionId,
    required this.serviceRequestId,
    required this.status,
    required this.pricingMode,
    required this.passengerUserId,
    required this.baselinePrice,
    required this.lowestBid,
    required this.bids,
    required this.counterOffers,
  });

  final String sessionId;
  final String serviceRequestId;
  final String status;
  final PricingMode? pricingMode;
  final String? passengerUserId;
  final double? baselinePrice;
  final double? lowestBid;
  final List<SBid> bids;
  final List<SCounterOffer> counterOffers;

  factory SBiddingSession.fromJson(Map<String, dynamic> json) {
    final sessionId = json['session_id']?.toString() ?? json['id']?.toString() ?? '';

    return SBiddingSession(
      sessionId: sessionId,
      serviceRequestId: json['service_request_id'] as String,
      status: json['status']?.toString() ?? '',
      pricingMode: _pricingMode(json['pricing_mode']),
      passengerUserId: json['passenger_user_id'] as String?,
      baselinePrice: _toDouble(json['baseline_price']),
      lowestBid: _toDouble(json['lowest_bid']),
      bids: _toList(json['bids'], SBid.fromJson),
      counterOffers: (json['counter_offers'] as List<dynamic>? ?? <dynamic>[])
          .map(
            (item) => SCounterOffer.fromJson(
              item as Map<String, dynamic>,
              fallbackSessionId: sessionId,
            ),
          )
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'session_id': sessionId,
      'service_request_id': serviceRequestId,
      'status': status,
      'pricing_mode': pricingMode?.value,
      'passenger_user_id': passengerUserId,
      'baseline_price': baselinePrice,
      'lowest_bid': lowestBid,
      'bids': bids.map((bid) => bid.toJson()).toList(),
      'counter_offers':
          counterOffers.map((offer) => offer.toJson()).toList(),
    };
  }
}

double? _toDouble(Object? value) {
  if (value == null) return null;
  if (value is double) return value;
  if (value is int) return value.toDouble();
  return double.parse(value.toString());
}

int? _toInt(Object? value) {
  if (value == null) return null;
  if (value is int) return value;
  return int.parse(value.toString());
}

DateTime? _toDateTime(Object? value) {
  if (value == null) return null;
  if (value is DateTime) return value;
  return DateTime.parse(value.toString());
}

PricingMode? _pricingMode(Object? value) {
  if (value == null) return null;
  return PricingMode.fromJson(value.toString());
}

List<T> _toList<T>(
  Object? value,
  T Function(Map<String, dynamic> json) fromJson,
) {
  final items = value as List<dynamic>? ?? <dynamic>[];
  return items.map((item) => fromJson(item as Map<String, dynamic>)).toList();
}
