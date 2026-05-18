import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import '../domain/location_models.dart';

class SGeospatialRepository {
  const SGeospatialRepository();

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

  Future<Map<String, dynamic>> validatePickup(SCoordinate coordinate) {
    return SHttpClient.post(
      '/validate-pickup',
      service: SApiService.geospatial,
      requiresAuth: true,
      body: coordinate.toJson(),
    );
  }

  Future<Map<String, dynamic>> getSurge(SCoordinate coordinate) {
    return SHttpClient.post(
      '/surge',
      service: SApiService.geospatial,
      requiresAuth: true,
      body: coordinate.toJson(),
    );
  }
}
