import 'demo/location_demo_data.dart';
import '../domain/location_models.dart';
import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';

class SLocationRepository {
  const SLocationRepository({bool? useDemoData})
      : _useDemoData = useDemoData ?? SApiConstants.useLocationDemoData;

  final bool _useDemoData;

  Future<SAddressResult> geocode(String address) async {
    if (_useDemoData) return SLocationDemoData.geocode(address);
    final data = await SHttpClient.post(
      '/geocode',
      service: SApiService.location,
      requiresAuth: true,
      body: {'address': address},
    );
    return SAddressResult.fromJson(data);
  }

  Future<List<SAddressResult>> searchPlaces(
    String query, {
    SCoordinate? proximity,
    int limit = 10,
  }) async {
    if (_useDemoData) return [SLocationDemoData.geocode(query)];
    final data = await SHttpClient.post(
      '/places/search',
      service: SApiService.location,
      requiresAuth: true,
      body: {
        'query': query,
        if (proximity != null) 'latitude': proximity.latitude,
        if (proximity != null) 'longitude': proximity.longitude,
        'limit': limit,
      },
    );
    final rawResults = data['results'];
    if (rawResults is! List) return const [];
    return rawResults
        .whereType<Map<String, dynamic>>()
        .map(SAddressResult.fromJson)
        .where((item) => item.formatted.isNotEmpty)
        .toList();
  }

  Future<SAddressResult> reverseGeocode(SCoordinate coordinate) async {
    if (_useDemoData) return SLocationDemoData.reverseGeocode(coordinate);
    final data = await SHttpClient.post(
      '/reverse',
      service: SApiService.location,
      requiresAuth: true,
      body: {
        'latitude': coordinate.latitude,
        'longitude': coordinate.longitude,
      },
    );
    return SAddressResult.fromJson(data);
  }

  Future<SLiveRideLocations> getRideLocations(String rideId) async {
    if (_useDemoData) return SLocationDemoData.liveRideLocations(rideId);
    final data = await SHttpClient.get(
      '/rides/$rideId/locations',
      service: SApiService.location,
      requiresAuth: true,
    );
    return SLiveRideLocations.fromJson(data);
  }
}
