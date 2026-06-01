import '../../../features/location/domain/location_models.dart';

class SMapController {
  SMapboxCameraReader? _cameraReader;
  SMapboxFlyToCallback? _flyTo;

  void attachCameraReader(SMapboxCameraReader cameraReader) {
    _cameraReader = cameraReader;
  }

  void attachFlyTo(SMapboxFlyToCallback flyTo) {
    _flyTo = flyTo;
  }

  Future<SCoordinate?> centerCoordinate() {
    return _cameraReader?.call() ?? Future.value();
  }

  Future<void> flyToCoordinate(SCoordinate coordinate) {
    return _flyTo?.call(coordinate) ?? Future.value();
  }
}

typedef SMapboxCameraReader = Future<SCoordinate?> Function();
typedef SMapboxFlyToCallback = Future<void> Function(SCoordinate coordinate);

enum SMapMarkerType {
  pickup,
  dropoff,
  driver,
  passenger,
}

enum SMapCameraMode {
  manual,
  staticPreview,
  fitRoute,
  followDriver,
  followUser,
  navigationFollow,
}

class SMapMarker {
  const SMapMarker({
    required this.id,
    required this.coordinate,
    required this.type,
    required this.label,
    this.isStale = false,
    this.heading,
  });

  final String id;
  final SCoordinate coordinate;
  final SMapMarkerType type;
  final String label;
  final bool isStale;
  final double? heading;
}
