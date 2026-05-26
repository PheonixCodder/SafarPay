import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import '../domain/driver_request_models.dart';
import '../../location/domain/location_models.dart';

class SDriverRequestsRepository {
  const SDriverRequestsRepository();

  Future<String?> fetchCurrentDriverId() async {
    final data = await SHttpClient.get(
      '/me',
      service: SApiService.verification,
      requiresAuth: true,
    );
    return data['driver_id']?.toString();
  }

  Future<void> setDriverStatus({
    required String driverId,
    required bool isOnline,
  }) {
    return SHttpClient.post(
      '/drivers/$driverId/status',
      service: SApiService.location,
      requiresAuth: true,
      body: {'status': isOnline ? 'ONLINE' : 'OFFLINE'},
    ).then((_) {});
  }

  Future<void> updateDriverLocation({
    required String driverId,
    required SCoordinate coordinate,
    double accuracy = 25,
    String? rideId,
  }) {
    return SHttpClient.post(
      '/drivers/$driverId/location',
      service: SApiService.location,
      requiresAuth: true,
      body: {
        'lat': coordinate.latitude,
        'lng': coordinate.longitude,
        'accuracy': accuracy,
        'ts': DateTime.now().millisecondsSinceEpoch,
        if (rideId != null) 'ride_id': rideId,
      },
    ).then((_) {});
  }

  Future<List<SDriverRideRequest>> fetchRequests({
    required SCoordinate coordinate,
    double radiusKm = 10,
    int limit = 20,
  }) async {
    final query = Uri(
      queryParameters: {
        'lat': coordinate.latitude.toString(),
        'lng': coordinate.longitude.toString(),
        'radius_km': radiusKm.toString(),
        'limit': limit.toString(),
      },
    ).query;
    final data = await SHttpClient.get(
      '/driver/requests?$query',
      service: SApiService.ride,
      requiresAuth: true,
    );
    final values = data['data'];
    if (values is! List) return const [];
    return values
        .whereType<Map<String, dynamic>>()
        .map(SDriverRideRequest.fromJson)
        .where((request) => request.id.isNotEmpty)
        .toList();
  }

  Future<SDriverActiveRide?> fetchActiveRide({
    SCoordinate? coordinate,
  }) async {
    final query = coordinate == null
        ? ''
        : '?${Uri(queryParameters: {
                'lat': coordinate.latitude.toString(),
                'lng': coordinate.longitude.toString(),
              }).query}';
    final data = await SHttpClient.get(
      '/driver/rides/active$query',
      service: SApiService.ride,
      requiresAuth: true,
    );
    if (data.isEmpty || data['id'] == null) return null;
    return SDriverActiveRide.fromJson(data);
  }
}
