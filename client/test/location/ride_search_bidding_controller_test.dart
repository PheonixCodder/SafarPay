import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/data/bidding_repository.dart';
import 'package:client/features/location/data/bidding_socket_event.dart';
import 'package:client/features/location/data/bidding_socket_repository.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('legacy flat bid event refreshes session bids for passenger matching UI',
      () async {
    final repository = _FakeBiddingRepository();
    final controller = SRideSearchController(biddingRepository: repository);
    controller.biddingSessionId.value = 'session-001';

    await controller.handleBiddingEvent(
      SBiddingSocketEvent.fromJson({
        'event': 'NEW_BID',
        'payload': {
          'session_id': 'session-001',
          'bid_id': 'bid-001',
          'amount': 340,
        },
      }),
    );

    expect(repository.getBidsForSessionCalls, 1);
    expect(controller.driverBids.single.id, 'bid-001');
  });

  test('resumes existing ride matching and connects passenger bidding socket',
      () async {
    final repository = _FakeBiddingRepository();
    final socketRepository = _FakeBiddingSocketRepository();
    final controller = SRideSearchController(
      biddingRepository: repository,
      biddingSocketRepository: socketRepository,
    );

    await controller.resumeMatchingForRide('ride-001');

    expect(controller.createdRideId.value, 'ride-001');
    expect(controller.biddingSessionId.value, 'session-001');
    expect(controller.sheetMode.value, SBookingSheetMode.matching);
    expect(controller.driverBids.single.id, 'bid-001');
    expect(repository.getSessionForRideCalls, 1);
    expect(repository.getBidsForSessionCalls, 1);
    expect(socketRepository.connectedSessionIds, ['session-001']);
  });
}

class _FakeBiddingRepository extends SBiddingRepository {
  int getBidsForSessionCalls = 0;
  int getSessionForRideCalls = 0;

  @override
  Future<Map<String, dynamic>> getSessionForRide(String rideId) async {
    getSessionForRideCalls += 1;
    return _sessionPayload('session-001', rideId);
  }

  @override
  Future<Map<String, dynamic>> getBidsForSession(String sessionId) async {
    getBidsForSessionCalls += 1;
    return _sessionPayload(sessionId, 'ride-001');
  }

  Map<String, dynamic> _sessionPayload(String sessionId, String rideId) {
    return {
      'session_id': sessionId,
      'service_request_id': rideId,
      'status': 'OPEN',
      'pricing_mode': 'HYBRID',
      'passenger_user_id': 'passenger-001',
      'baseline_price': 400,
      'lowest_bid': 340,
      'bids': [
        {
          'id': 'bid-001',
          'bidding_session_id': sessionId,
          'driver_id': 'driver-001',
          'driver_vehicle_id': null,
          'bid_amount': 340,
          'currency': 'PKR',
          'eta_minutes': 4,
          'message': 'Driver offer',
          'status': 'ACTIVE',
          'placed_at': '2026-05-24T12:00:00Z',
        },
      ],
      'counter_offers': const [],
    };
  }
}

class _FakeBiddingSocketRepository extends SBiddingSocketRepository {
  final List<String> connectedSessionIds = <String>[];

  @override
  Stream<SBiddingSocketEvent> connectPassenger({required String sessionId}) {
    connectedSessionIds.add(sessionId);
    return const Stream<SBiddingSocketEvent>.empty();
  }
}
