import '../../../features/location/domain/location_models.dart';

class SMapController {
  SMapboxCameraReader? _cameraReader;

  void attachCameraReader(SMapboxCameraReader cameraReader) {
    _cameraReader = cameraReader;
  }

  Future<SCoordinate?> centerCoordinate() {
    return _cameraReader?.call() ?? Future.value();
  }
}

typedef SMapboxCameraReader = Future<SCoordinate?> Function();

enum SMapMarkerType {
  pickup,
  dropoff,
  driver,
  passenger,
}

class SMapMarker {
  const SMapMarker({
    required this.id,
    required this.coordinate,
    required this.type,
    required this.label,
    this.isStale = false,
  });

  final String id;
  final SCoordinate coordinate;
  final SMapMarkerType type;
  final String label;
  final bool isStale;
}
