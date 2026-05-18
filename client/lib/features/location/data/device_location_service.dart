import 'dart:async';

import 'package:geolocator/geolocator.dart';

import '../domain/location_models.dart';

class SDeviceLocationService {
  const SDeviceLocationService();

  Future<SCoordinate> currentCoordinate() async {
    await _ensureReady();
    final position = await Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        timeLimit: Duration(seconds: 12),
      ),
    );
    return _toCoordinate(position);
  }

  Stream<SCoordinate> positionStream() async* {
    await _ensureReady();
    yield* Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10,
      ),
    ).map(_toCoordinate);
  }

  Future<void> _ensureReady() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw const SLocationUnavailableException(
        'Location services are disabled.',
      );
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      throw const SLocationUnavailableException(
        'Location permission is required.',
      );
    }
  }

  SCoordinate _toCoordinate(Position position) {
    return SCoordinate(
      latitude: position.latitude,
      longitude: position.longitude,
    );
  }
}

class SLocationUnavailableException implements Exception {
  const SLocationUnavailableException(this.message);

  final String message;

  @override
  String toString() => message;
}
