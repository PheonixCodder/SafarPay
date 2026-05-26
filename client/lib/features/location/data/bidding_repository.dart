import 'demo/location_demo_data.dart';
import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';

class SBiddingRepository {
  const SBiddingRepository({bool? useDemoData})
      : _useDemoData = useDemoData ?? SApiConstants.useLocationDemoData;

  final bool _useDemoData;

  Future<Map<String, dynamic>> getBidsForSession(String sessionId) {
    if (_useDemoData) {
      return Future.value(SLocationDemoData.hybridSession('demo-ride-001'));
    }
    return SHttpClient.get(
      '/sessions/$sessionId',
      service: SApiService.bidding,
      requiresAuth: true,
    );
  }

  Future<Map<String, dynamic>> placeBid({
    required String sessionId,
    required double bidAmount,
    String? driverVehicleId,
    int? etaMinutes,
    String? message,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.placedBid(
          sessionId: sessionId,
          bidAmount: bidAmount,
          driverVehicleId: driverVehicleId,
          etaMinutes: etaMinutes,
          message: message,
        ),
      );
    }
    return SHttpClient.post(
      '/sessions/$sessionId/bids',
      service: SApiService.bidding,
      requiresAuth: true,
      body: {
        if (driverVehicleId != null) 'driver_vehicle_id': driverVehicleId,
        'bid_amount': bidAmount,
        if (etaMinutes != null) 'eta_minutes': etaMinutes,
        if (message != null) 'message': message,
      },
    );
  }

  Future<Map<String, dynamic>> acceptBid({
    required String sessionId,
    required String bidId,
  }) {
    if (_useDemoData) {
      return Future.value(SLocationDemoData.acceptedBid(sessionId, bidId));
    }
    return SHttpClient.post(
      '/sessions/$sessionId/accept',
      service: SApiService.bidding,
      requiresAuth: true,
      body: {'bid_id': bidId},
    );
  }

  Future<Map<String, dynamic>> getSessionForRide(String rideId) {
    if (_useDemoData) {
      return Future.value(SLocationDemoData.hybridSession(rideId));
    }
    return SHttpClient.get(
      '/sessions/by-ride/$rideId',
      service: SApiService.bidding,
      requiresAuth: true,
    );
  }

  Future<Map<String, dynamic>> withdrawBid({
    required String sessionId,
    required String bidId,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.withdrawnBid(sessionId: sessionId, bidId: bidId),
      );
    }
    return SHttpClient.post(
      '/sessions/$sessionId/bids/$bidId/withdraw',
      service: SApiService.bidding,
      requiresAuth: true,
    );
  }

  Future<Map<String, dynamic>> sendPassengerCounter({
    required String sessionId,
    required double counterPrice,
    int? counterEtaMinutes,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.counterOffer(
          sessionId: sessionId,
          counterPrice: counterPrice,
          counterEtaMinutes: counterEtaMinutes,
        ),
      );
    }
    return SHttpClient.post(
      '/sessions/$sessionId/passenger-counter',
      service: SApiService.bidding,
      requiresAuth: true,
      body: {
        'counter_price': counterPrice,
        if (counterEtaMinutes != null) 'counter_eta_minutes': counterEtaMinutes,
      },
    );
  }

  Future<Map<String, dynamic>> acceptPassengerCounter({
    required String sessionId,
    required String counterOfferId,
  }) {
    if (_useDemoData) {
      return Future.value(
        SLocationDemoData.acceptedCounter(
          sessionId: sessionId,
          counterOfferId: counterOfferId,
        ),
      );
    }
    return SHttpClient.post(
      '/sessions/$sessionId/counter/$counterOfferId/accept',
      service: SApiService.bidding,
      requiresAuth: true,
    );
  }

  Future<List<dynamic>> getCounterOffers(String sessionId) async {
    if (_useDemoData) return SLocationDemoData.counterOffers(sessionId);
    final data = await SHttpClient.get(
      '/sessions/$sessionId/counter-offers',
      service: SApiService.bidding,
      requiresAuth: true,
    );
    final values = data['data'];
    return values is List ? values : const [];
  }
}
