import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';

class SBiddingRepository {
  const SBiddingRepository();

  Future<Map<String, dynamic>> getBidsForSession(String sessionId) {
    return SHttpClient.get(
      '/sessions/$sessionId',
      service: SApiService.bidding,
      requiresAuth: true,
    );
  }

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
