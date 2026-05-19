import 'demo/location_demo_data.dart';
import '../domain/location_models.dart';

class SGeospatialRepository {
  const SGeospatialRepository();

  Future<SRoutePreview> calculateRoute({
    required SCoordinate origin,
    required SCoordinate destination,
  }) async {
    return SLocationDemoData.routePreview;
    // final data = await SHttpClient.post(
    //   '/routes',
    //   service: SApiService.geospatial,
    //   requiresAuth: true,
    //   body: {
    //     'origin': origin.toJson(),
    //     'destination': destination.toJson(),
    //   },
    // );
    // return SRoutePreview.fromJson(data);
  }

  Future<Map<String, dynamic>> validatePickup(SCoordinate coordinate) {
    return Future.value(SLocationDemoData.pickupValidation(coordinate));
    // return SHttpClient.post(
    //   '/validate-pickup',
    //   service: SApiService.geospatial,
    //   requiresAuth: true,
    //   body: coordinate.toJson(),
    // );
  }

  Future<Map<String, dynamic>> getSurge(SCoordinate coordinate) {
    return Future.value(SLocationDemoData.surge(coordinate));
    // return SHttpClient.post(
    //   '/surge',
    //   service: SApiService.geospatial,
    //   requiresAuth: true,
    //   body: coordinate.toJson(),
    // );
  }
}
