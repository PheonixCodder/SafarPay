import 'demo/location_demo_data.dart';
import '../../../common/runtime/runtime_mode.dart';
import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';

class SBiddingRepository {
  const SBiddingRepository({bool? useDemoData})
      : _delegate = (useDemoData ?? SRuntimeModeConfig.useLocationDemoData)
            ? const _DemoBiddingRepository()
            : const _HttpBiddingRepository();

  final _BiddingRepositoryDelegate _delegate;

  SRuntimeDataSource get runtimeDataSource => _delegate.runtimeDataSource;

  Future<Map<String, dynamic>> getBidsForSession(String sessionId) {
    return _delegate.getBidsForSession(sessionId);
  }

  Future<Map<String, dynamic>> placeBid({
    required String sessionId,
    required double bidAmount,
    String? driverVehicleId,
    int? etaMinutes,
    String? message,
  }) {
    return _delegate.placeBid(
      sessionId: sessionId,
      bidAmount: bidAmount,
      driverVehicleId: driverVehicleId,
      etaMinutes: etaMinutes,
      message: message,
    );
  }

  Future<Map<String, dynamic>> acceptBid({
    required String sessionId,
    required String bidId,
  }) {
    return _delegate.acceptBid(sessionId: sessionId, bidId: bidId);
  }

  Future<Map<String, dynamic>> getSessionForRide(String rideId) {
    return _delegate.getSessionForRide(rideId);
  }

  Future<Map<String, dynamic>> withdrawBid({
    required String sessionId,
    required String bidId,
  }) {
    return _delegate.withdrawBid(sessionId: sessionId, bidId: bidId);
  }

  Future<Map<String, dynamic>> sendPassengerCounter({
    required String sessionId,
    required double counterPrice,
    int? counterEtaMinutes,
  }) {
    return _delegate.sendPassengerCounter(
      sessionId: sessionId,
      counterPrice: counterPrice,
      counterEtaMinutes: counterEtaMinutes,
    );
  }

  Future<Map<String, dynamic>> acceptPassengerCounter({
    required String sessionId,
    required String counterOfferId,
  }) {
    return _delegate.acceptPassengerCounter(
      sessionId: sessionId,
      counterOfferId: counterOfferId,
    );
  }

  Future<List<dynamic>> getCounterOffers(String sessionId) async {
    return _delegate.getCounterOffers(sessionId);
  }
}

abstract class _BiddingRepositoryDelegate {
  const _BiddingRepositoryDelegate();

  SRuntimeDataSource get runtimeDataSource;

  Future<Map<String, dynamic>> getBidsForSession(String sessionId);

  Future<Map<String, dynamic>> placeBid({
    required String sessionId,
    required double bidAmount,
    String? driverVehicleId,
    int? etaMinutes,
    String? message,
  });

  Future<Map<String, dynamic>> acceptBid({
    required String sessionId,
    required String bidId,
  });

  Future<Map<String, dynamic>> getSessionForRide(String rideId);

  Future<Map<String, dynamic>> withdrawBid({
    required String sessionId,
    required String bidId,
  });

  Future<Map<String, dynamic>> sendPassengerCounter({
    required String sessionId,
    required double counterPrice,
    int? counterEtaMinutes,
  });

  Future<Map<String, dynamic>> acceptPassengerCounter({
    required String sessionId,
    required String counterOfferId,
  });

  Future<List<dynamic>> getCounterOffers(String sessionId);
}

class _DemoBiddingRepository extends _BiddingRepositoryDelegate {
  const _DemoBiddingRepository();

  @override
  SRuntimeDataSource get runtimeDataSource => SRuntimeDataSource.demo;

  @override
  Future<Map<String, dynamic>> getBidsForSession(String sessionId) {
    return Future.value(SLocationDemoData.hybridSession('demo-ride-001'));
  }

  @override
  Future<Map<String, dynamic>> placeBid({
    required String sessionId,
    required double bidAmount,
    String? driverVehicleId,
    int? etaMinutes,
    String? message,
  }) {
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

  @override
  Future<Map<String, dynamic>> acceptBid({
    required String sessionId,
    required String bidId,
  }) {
    return Future.value(SLocationDemoData.acceptedBid(sessionId, bidId));
  }

  @override
  Future<Map<String, dynamic>> getSessionForRide(String rideId) {
    return Future.value(SLocationDemoData.hybridSession(rideId));
  }

  @override
  Future<Map<String, dynamic>> withdrawBid({
    required String sessionId,
    required String bidId,
  }) {
    return Future.value(
      SLocationDemoData.withdrawnBid(sessionId: sessionId, bidId: bidId),
    );
  }

  @override
  Future<Map<String, dynamic>> sendPassengerCounter({
    required String sessionId,
    required double counterPrice,
    int? counterEtaMinutes,
  }) {
    return Future.value(
      SLocationDemoData.counterOffer(
        sessionId: sessionId,
        counterPrice: counterPrice,
        counterEtaMinutes: counterEtaMinutes,
      ),
    );
  }

  @override
  Future<Map<String, dynamic>> acceptPassengerCounter({
    required String sessionId,
    required String counterOfferId,
  }) {
    return Future.value(
      SLocationDemoData.acceptedCounter(
        sessionId: sessionId,
        counterOfferId: counterOfferId,
      ),
    );
  }

  @override
  Future<List<dynamic>> getCounterOffers(String sessionId) {
    return Future.value(SLocationDemoData.counterOffers(sessionId));
  }
}

class _HttpBiddingRepository extends _BiddingRepositoryDelegate {
  const _HttpBiddingRepository();

  @override
  SRuntimeDataSource get runtimeDataSource => SRuntimeDataSource.real;

  @override
  Future<Map<String, dynamic>> getBidsForSession(String sessionId) {
    return SHttpClient.get(
      '/sessions/$sessionId',
      service: SApiService.bidding,
      requiresAuth: true,
    );
  }

  @override
  Future<Map<String, dynamic>> placeBid({
    required String sessionId,
    required double bidAmount,
    String? driverVehicleId,
    int? etaMinutes,
    String? message,
  }) {
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

  @override
  Future<Map<String, dynamic>> acceptBid({
    required String sessionId,
    required String bidId,
  }) {
    return SHttpClient.post(
      '/sessions/$sessionId/accept',
      service: SApiService.bidding,
      requiresAuth: true,
      body: {'bid_id': bidId},
    );
  }

  @override
  Future<Map<String, dynamic>> getSessionForRide(String rideId) {
    return SHttpClient.get(
      '/sessions/by-ride/$rideId',
      service: SApiService.bidding,
      requiresAuth: true,
    );
  }

  @override
  Future<Map<String, dynamic>> withdrawBid({
    required String sessionId,
    required String bidId,
  }) {
    return SHttpClient.post(
      '/sessions/$sessionId/bids/$bidId/withdraw',
      service: SApiService.bidding,
      requiresAuth: true,
    );
  }

  @override
  Future<Map<String, dynamic>> sendPassengerCounter({
    required String sessionId,
    required double counterPrice,
    int? counterEtaMinutes,
  }) {
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

  @override
  Future<Map<String, dynamic>> acceptPassengerCounter({
    required String sessionId,
    required String counterOfferId,
  }) {
    return SHttpClient.post(
      '/sessions/$sessionId/counter/$counterOfferId/accept',
      service: SApiService.bidding,
      requiresAuth: true,
    );
  }

  @override
  Future<List<dynamic>> getCounterOffers(String sessionId) async {
    final data = await SHttpClient.get(
      '/sessions/$sessionId/counter-offers',
      service: SApiService.bidding,
      requiresAuth: true,
    );
    final values = data['data'];
    return values is List ? values : const [];
  }
}
