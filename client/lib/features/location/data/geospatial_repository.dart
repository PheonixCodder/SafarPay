import 'demo/location_demo_data.dart';
import '../../../common/runtime/runtime_mode.dart';
import '../domain/location_models.dart';
import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';

class SGeospatialRepository {
  const SGeospatialRepository({bool? useDemoData})
      : _delegate = (useDemoData ?? SRuntimeModeConfig.useLocationDemoData)
            ? const _DemoGeospatialRepository()
            : const _HttpGeospatialRepository();

  final _GeospatialRepositoryDelegate _delegate;

  SRuntimeDataSource get runtimeDataSource => _delegate.runtimeDataSource;

  Future<SRoutePreview> calculateRoute({
    required SCoordinate origin,
    required SCoordinate destination,
  }) async {
    return _delegate.calculateRoute(origin: origin, destination: destination);
  }

  Future<Map<String, dynamic>> validatePickup(SCoordinate coordinate) {
    return _delegate.validatePickup(coordinate);
  }

  Future<Map<String, dynamic>> getSurge(SCoordinate coordinate) {
    return _delegate.getSurge(coordinate);
  }
}

abstract class _GeospatialRepositoryDelegate {
  const _GeospatialRepositoryDelegate();

  SRuntimeDataSource get runtimeDataSource;

  Future<SRoutePreview> calculateRoute({
    required SCoordinate origin,
    required SCoordinate destination,
  });

  Future<Map<String, dynamic>> validatePickup(SCoordinate coordinate);

  Future<Map<String, dynamic>> getSurge(SCoordinate coordinate);
}

class _DemoGeospatialRepository extends _GeospatialRepositoryDelegate {
  const _DemoGeospatialRepository();

  @override
  SRuntimeDataSource get runtimeDataSource => SRuntimeDataSource.demo;

  @override
  Future<SRoutePreview> calculateRoute({
    required SCoordinate origin,
    required SCoordinate destination,
  }) async {
    return SLocationDemoData.routePreview;
  }

  @override
  Future<Map<String, dynamic>> validatePickup(SCoordinate coordinate) {
    return Future.value(SLocationDemoData.pickupValidation(coordinate));
  }

  @override
  Future<Map<String, dynamic>> getSurge(SCoordinate coordinate) {
    return Future.value(SLocationDemoData.surge(coordinate));
  }
}

class _HttpGeospatialRepository extends _GeospatialRepositoryDelegate {
  const _HttpGeospatialRepository();

  @override
  SRuntimeDataSource get runtimeDataSource => SRuntimeDataSource.real;

  @override
  Future<SRoutePreview> calculateRoute({
    required SCoordinate origin,
    required SCoordinate destination,
  }) async {
    final data = await SHttpClient.post(
      '/routes',
      service: SApiService.geospatial,
      requiresAuth: true,
      body: {
        'origin': origin.toJson(),
        'destination': destination.toJson(),
      },
    );
    return SRoutePreview.fromJson(data);
  }

  @override
  Future<Map<String, dynamic>> validatePickup(SCoordinate coordinate) {
    return SHttpClient.post(
      '/validate-pickup',
      service: SApiService.geospatial,
      requiresAuth: true,
      body: coordinate.toJson(),
    );
  }

  @override
  Future<Map<String, dynamic>> getSurge(SCoordinate coordinate) {
    return SHttpClient.post(
      '/surge',
      service: SApiService.geospatial,
      requiresAuth: true,
      body: coordinate.toJson(),
    );
  }
}
