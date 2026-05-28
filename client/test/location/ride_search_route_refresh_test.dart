import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/data/geospatial_repository.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('loading a new route clears stale route geometry first', () async {
    final geospatialRepository = _DelayedGeospatialRepository();
    final controller = SRideSearchController(
      geospatialRepository: geospatialRepository,
    );

    controller.pickup.value = const SAddressResult(
      formatted: 'Pickup',
      coordinate: SCoordinate(latitude: 31.52, longitude: 74.35),
    );
    controller.selectedDropoff.value = const SAddressResult(
      formatted: 'Dropoff',
      coordinate: SCoordinate(latitude: 31.6, longitude: 74.4),
    );
    controller.route.value = const SRoutePreview(
      distanceKm: 1,
      durationMinutes: 2,
      polyline: '_p~iF~ps|U_ulLnnqC_mqNvxq`@',
      steps: [],
    );

    final routeFuture = controller.loadRoutePreview();

    expect(controller.route.value, isNull);

    await routeFuture;

    expect(controller.route.value?.polyline, 'new-route');
  });
}

class _DelayedGeospatialRepository extends SGeospatialRepository {
  @override
  Future<SRoutePreview> calculateRoute({
    required SCoordinate origin,
    required SCoordinate destination,
  }) async {
    await Future<void>.delayed(const Duration(milliseconds: 20));
    return const SRoutePreview(
      distanceKm: 4,
      durationMinutes: 8,
      polyline: 'new-route',
      steps: [],
    );
  }
}
