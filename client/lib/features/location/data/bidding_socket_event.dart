import '../domain/bidding_models.dart';

enum SBiddingSocketEventType {
  bidPlaced,
  bidAccepted,
  bidWithdrawn,
  counterOfferCreated,
  counterOfferAccepted,
  sessionUpdated,
  ping,
  pong,
  error,
  unknown,
}

class SBiddingSocketEvent {
  const SBiddingSocketEvent({
    required this.type,
    this.sessionId,
    this.bid,
    this.counterOffer,
    this.data,
    this.detail,
  });

  final SBiddingSocketEventType type;
  final String? sessionId;
  final SBid? bid;
  final SCounterOffer? counterOffer;
  final Map<String, dynamic>? data;
  final String? detail;

  factory SBiddingSocketEvent.fromJson(Map<String, dynamic> json) {
    final event = json['event']?.toString();
    final data = _modelJson(json, 'data') ?? _modelJson(json, 'payload');
    final bidJson = _modelJson(data, 'bid') ?? _modelJson(json, 'bid');
    final counterJson =
        _modelJson(data, 'counter_offer') ?? _modelJson(json, 'counter_offer');
    final sessionId = _stringValue(data, 'session_id') ??
        _stringValue(json, 'session_id') ??
        _stringValue(bidJson, 'bidding_session_id') ??
        _stringValue(counterJson, 'session_id');

    return SBiddingSocketEvent(
      type: _typeFor(event),
      sessionId: sessionId,
      bid: bidJson == null ? null : SBid.fromJson(bidJson),
      counterOffer: counterJson == null
          ? null
          : SCounterOffer.fromJson(counterJson, fallbackSessionId: sessionId),
      data: data,
      detail: json['detail']?.toString() ?? json['message']?.toString(),
    );
  }
}

SBiddingSocketEventType _typeFor(String? event) {
  return switch (event) {
    'NEW_BID' ||
    'BID_PLACED' => SBiddingSocketEventType.bidPlaced,
    'BID_ACCEPTED' => SBiddingSocketEventType.bidAccepted,
    'BID_WITHDRAWN' => SBiddingSocketEventType.bidWithdrawn,
    'PASSENGER_COUNTER_BID' ||
    'PASSENGER_COUNTER_OFFER_CREATED' ||
    'COUNTER_OFFER_CREATED' =>
      SBiddingSocketEventType.counterOfferCreated,
    'PASSENGER_COUNTER_OFFER_ACCEPTED' ||
    'COUNTER_OFFER_ACCEPTED' =>
      SBiddingSocketEventType.counterOfferAccepted,
    'BID_LEADER_UPDATED' ||
    'SESSION_CLOSED' ||
    'SESSION_CANCELLED' ||
    'SESSION_UPDATED' =>
      SBiddingSocketEventType.sessionUpdated,
    'ping' => SBiddingSocketEventType.ping,
    'pong' => SBiddingSocketEventType.pong,
    'error' => SBiddingSocketEventType.error,
    _ => SBiddingSocketEventType.unknown,
  };
}

Map<String, dynamic>? _modelJson(Map<String, dynamic>? json, String key) {
  final value = json?[key];
  return value is Map<String, dynamic> ? value : null;
}

String? _stringValue(Map<String, dynamic>? json, String key) {
  return json?[key]?.toString();
}
