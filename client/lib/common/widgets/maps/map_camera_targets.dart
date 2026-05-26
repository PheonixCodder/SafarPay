import '../../../features/location/domain/location_models.dart';
import 'map_models.dart';
import 'map_route_geometry.dart';

class SMapCameraTargets {
  const SMapCameraTargets._();

  static List<SCoordinate> coordinates({
    required SMapCameraMode mode,
    required SRoutePreview? route,
    required List<SMapMarker> markers,
  }) {
    if (mode == SMapCameraMode.navigationFollow) {
      final driverCoordinate = _firstMarkerCoordinate(
        markers,
        SMapMarkerType.driver,
      );
      if (driverCoordinate != null) return [driverCoordinate];
    }

    final routeCoordinates = SMapRouteGeometry.coordinatesForRoute(
      route: route,
      markers: markers
          .map(
            (marker) => SMapRoutePoint(
              id: marker.id,
              coordinate: marker.coordinate,
              isPickup: marker.type == SMapMarkerType.pickup,
            ),
          )
          .toList(),
    );
    if (routeCoordinates.length >= 2) return routeCoordinates;

    if (mode == SMapCameraMode.followDriver) {
      final driverCoordinate = _firstMarkerCoordinate(
        markers,
        SMapMarkerType.driver,
      );
      if (driverCoordinate != null) return [driverCoordinate];
    }

    if (mode == SMapCameraMode.followUser) {
      final userCoordinate = _firstMarkerCoordinate(
        markers,
        SMapMarkerType.passenger,
      );
      if (userCoordinate != null) return [userCoordinate];
    }

    return markers.map((marker) => marker.coordinate).toList();
  }

  static SCoordinate? _firstMarkerCoordinate(
    List<SMapMarker> markers,
    SMapMarkerType type,
  ) {
    for (final marker in markers) {
      if (marker.type == type) return marker.coordinate;
    }
    return null;
  }
}
