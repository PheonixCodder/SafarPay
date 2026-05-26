import 'demo/location_demo_data.dart';
import '../domain/location_models.dart';
import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';

class SGeospatialRepository {
  const SGeospatialRepository({bool? useDemoData})
      : _useDemoData = useDemoData ?? SApiConstants.useLocationDemoData;

  final bool _useDemoData;

  Future<SRoutePreview> calculateRoute({
    required SCoordinate origin,
    required SCoordinate destination,
  }) async {
    if (_useDemoData) return SLocationDemoData.routePreview;
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

  Future<Map<String, dynamic>> validatePickup(SCoordinate coordinate) {
    if (_useDemoData) {
      return Future.value(SLocationDemoData.pickupValidation(coordinate));
    }
    return SHttpClient.post(
      '/validate-pickup',
      service: SApiService.geospatial,
      requiresAuth: true,
      body: coordinate.toJson(),
    );
  }

  Future<Map<String, dynamic>> getSurge(SCoordinate coordinate) {
    if (_useDemoData) return Future.value(SLocationDemoData.surge(coordinate));
    return SHttpClient.post(
      '/surge',
      service: SApiService.geospatial,
      requiresAuth: true,
      body: coordinate.toJson(),
    );
  }
}
