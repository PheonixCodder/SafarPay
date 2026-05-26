import '../../../features/location/domain/location_models.dart';

class SMapRoutePoint {
  const SMapRoutePoint({
    required this.id,
    required this.coordinate,
    required this.isPickup,
  });

  final String id;
  final SCoordinate coordinate;
  final bool isPickup;
}

class SMapRouteGeometry {
  const SMapRouteGeometry._();

  static List<SCoordinate> coordinatesForRoute({
    required SRoutePreview? route,
    required List<SMapRoutePoint> markers,
  }) {
    final routeCoordinates = _decodePolyline(route?.polyline ?? '');
    if (routeCoordinates.length >= 2) return routeCoordinates;

    return const [];
  }

  static List<SCoordinate> _decodePolyline(String polyline) {
    if (polyline.isEmpty) return const [];

    final coordinates = <SCoordinate>[];
    var index = 0;
    var latitude = 0;
    var longitude = 0;

    try {
      while (index < polyline.length) {
        final latitudeResult = _decodeNextValue(polyline, index);
        index = latitudeResult.nextIndex;
        latitude += latitudeResult.value;

        final longitudeResult = _decodeNextValue(polyline, index);
        index = longitudeResult.nextIndex;
        longitude += longitudeResult.value;

        coordinates.add(
          SCoordinate(
            latitude: latitude / 1e5,
            longitude: longitude / 1e5,
          ),
        );
      }
    } catch (_) {
      return const [];
    }

    return coordinates;
  }

  static _PolylineValue _decodeNextValue(String polyline, int startIndex) {
    var result = 0;
    var shift = 0;
    var index = startIndex;
    var byte = 0;

    do {
      if (index >= polyline.length) throw const FormatException();
      byte = polyline.codeUnitAt(index++) - 63;
      result |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);

    final value = (result & 1) == 1 ? ~(result >> 1) : result >> 1;
    return _PolylineValue(value: value, nextIndex: index);
  }

}

class _PolylineValue {
  const _PolylineValue({
    required this.value,
    required this.nextIndex,
  });

  final int value;
  final int nextIndex;
}
