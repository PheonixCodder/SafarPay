import '../../../features/location/domain/location_models.dart';

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
