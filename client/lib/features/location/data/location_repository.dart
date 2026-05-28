import 'demo/location_demo_data.dart';
import '../../../common/runtime/runtime_mode.dart';
import '../domain/location_models.dart';
import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';

class SLocationRepository {
  const SLocationRepository({bool? useDemoData})
      : _delegate = (useDemoData ?? SRuntimeModeConfig.useLocationDemoData)
            ? const _DemoLocationRepository()
            : const _HttpLocationRepository();

  final _LocationRepositoryDelegate _delegate;

  SRuntimeDataSource get runtimeDataSource => _delegate.runtimeDataSource;

  Future<SAddressResult> geocode(String address) async {
    return _delegate.geocode(address);
  }

  Future<List<SAddressResult>> searchPlaces(
    String query, {
    SCoordinate? proximity,
    int limit = 10,
  }) async {
    return _delegate.searchPlaces(query, proximity: proximity, limit: limit);
  }

  Future<SAddressResult> reverseGeocode(SCoordinate coordinate) async {
    return _delegate.reverseGeocode(coordinate);
  }

  Future<SLiveRideLocations> getRideLocations(String rideId) async {
    return _delegate.getRideLocations(rideId);
  }
}

abstract class _LocationRepositoryDelegate {
  const _LocationRepositoryDelegate();

  SRuntimeDataSource get runtimeDataSource;

  Future<SAddressResult> geocode(String address);

  Future<List<SAddressResult>> searchPlaces(
    String query, {
    SCoordinate? proximity,
    int limit = 10,
  });

  Future<SAddressResult> reverseGeocode(SCoordinate coordinate);

  Future<SLiveRideLocations> getRideLocations(String rideId);
}

class _DemoLocationRepository extends _LocationRepositoryDelegate {
  const _DemoLocationRepository();

  @override
  SRuntimeDataSource get runtimeDataSource => SRuntimeDataSource.demo;

  @override
  Future<SAddressResult> geocode(String address) async {
    return SLocationDemoData.geocode(address);
  }

  @override
  Future<List<SAddressResult>> searchPlaces(
    String query, {
    SCoordinate? proximity,
    int limit = 10,
  }) async {
    return [SLocationDemoData.geocode(query)];
  }

  @override
  Future<SAddressResult> reverseGeocode(SCoordinate coordinate) async {
    return SLocationDemoData.reverseGeocode(coordinate);
  }

  @override
  Future<SLiveRideLocations> getRideLocations(String rideId) async {
    return SLocationDemoData.liveRideLocations(rideId);
  }
}

class _HttpLocationRepository extends _LocationRepositoryDelegate {
  const _HttpLocationRepository();

  @override
  SRuntimeDataSource get runtimeDataSource => SRuntimeDataSource.real;

  @override
  Future<SAddressResult> geocode(String address) async {
    final data = await SHttpClient.post(
      '/geocode',
      service: SApiService.location,
      requiresAuth: true,
      body: {'address': address},
    );
    return SAddressResult.fromJson(data);
  }

  @override
  Future<List<SAddressResult>> searchPlaces(
    String query, {
    SCoordinate? proximity,
    int limit = 10,
  }) async {
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

  @override
  Future<SAddressResult> reverseGeocode(SCoordinate coordinate) async {
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

  @override
  Future<SLiveRideLocations> getRideLocations(String rideId) async {
    final data = await SHttpClient.get(
      '/rides/$rideId/locations',
      service: SApiService.location,
      requiresAuth: true,
    );
    return SLiveRideLocations.fromJson(data);
  }
}
