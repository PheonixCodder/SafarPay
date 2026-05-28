import 'dart:async';

import 'package:client/features/location/controllers/ride_tracking_controller.dart';
import 'package:client/features/location/data/device_location_service.dart';
import 'package:client/features/location/data/geospatial_repository.dart';
import 'package:client/features/location/data/live_ride_socket_event.dart';
import 'package:client/features/location/data/live_ride_socket_repository.dart';
import 'package:client/features/location/data/location_repository.dart';
import 'package:client/features/location/data/ride_repository.dart';
import 'package:client/features/location/data/ride_socket_event.dart';
import 'package:client/features/location/data/ride_socket_repository.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('matching unassigned ride does not open live location tracking',
      () async {
    final locationRepository = _LocationRepositorySpy();
    final liveSocketRepository = _LiveRideSocketRepositorySpy();
    final rideSocketRepository = _RideSocketRepositorySpy();
    final controller = SRideTrackingController(
      rideId: 'ride-001',
      locationRepository: locationRepository,
      rideRepository: _RideRepositoryStub(
        status: 'MATCHING',
        assignedDriverId: null,
      ),
      geospatialRepository: _GeospatialRepositoryStub(),
      socketRepository: liveSocketRepository,
      rideSocketRepository: rideSocketRepository,
      deviceLocationService: _DeviceLocationServiceStub(),
    );

    await controller.connect();
    await Future<void>.delayed(Duration.zero);

    expect(locationRepository.calls, 0);
    expect(liveSocketRepository.calls, 0);
    expect(rideSocketRepository.calls, 1);
    expect(controller.statusMessage.value, 'Waiting for a driver to accept.');

    controller.onClose();
  });
}

class _RideRepositoryStub extends SRideRepository {
  const _RideRepositoryStub({
    required this.status,
    required this.assignedDriverId,
  });

  final String status;
  final String? assignedDriverId;

  @override
  Future<Map<String, dynamic>> fetchRide(String rideId) async {
    return {
      'id': rideId,
      'passenger_id': 'passenger-001',
      'assigned_driver_id': assignedDriverId,
      'service_type': 'CITY_RIDE',
      'category': 'MINI',
      'pricing_mode': 'FIXED',
      'status': status,
      'baseline_min_price': 200,
      'baseline_max_price': 250,
      'final_price': null,
      'passenger_payment_method': 'CASH',
      'passenger_payment_method_id': null,
      'payment_collection_mode': 'DRIVER_COLLECTED',
      'scheduled_at': null,
      'is_scheduled': false,
      'is_risky': false,
      'auto_accept_driver': false,
      'accepted_at': null,
      'completed_at': null,
      'cancelled_at': null,
      'cancellation_reason': null,
      'created_at': '2026-05-26T10:00:00Z',
      'stops': const [],
      'proof_images': const [],
      'verification_codes': const [],
      'pickup_stop': _stop('PICKUP'),
      'dropoff_stop': _stop('DROPOFF'),
    };
  }
}

class _LocationRepositorySpy extends SLocationRepository {
  int calls = 0;

  @override
  Future<SLiveRideLocations> getRideLocations(String rideId) async {
    calls += 1;
    return SLiveRideLocations(
      rideId: rideId,
      driver: null,
      passenger: null,
    );
  }
}

class _LiveRideSocketRepositorySpy extends SLiveRideSocketRepository {
  int calls = 0;

  @override
  Stream<SLiveRideSocketEvent> connect(String rideId) async* {
    calls += 1;
  }
}

class _RideSocketRepositorySpy extends SRideSocketRepository {
  int calls = 0;

  @override
  Stream<SRideSocketEvent> connectPassenger({String? rideId}) async* {
    calls += 1;
  }
}

class _DeviceLocationServiceStub extends SDeviceLocationService {
  @override
  Future<SCoordinate> currentCoordinate() async {
    return const SCoordinate(latitude: 31.5, longitude: 74.3);
  }

  @override
  Stream<SCoordinate> positionStream() {
    return const Stream<SCoordinate>.empty();
  }
}

class _GeospatialRepositoryStub extends SGeospatialRepository {
  @override
  Future<SRoutePreview> calculateRoute({
    required SCoordinate origin,
    required SCoordinate destination,
  }) async {
    return const SRoutePreview(
      distanceKm: 0,
      durationMinutes: 0,
      polyline: '',
      steps: [],
    );
  }
}

Map<String, dynamic> _stop(String type) {
  return {
    'id': '$type-stop',
    'service_request_id': 'ride-001',
    'sequence_order': type == 'PICKUP' ? 1 : 2,
    'stop_type': type,
    'latitude': 31.5,
    'longitude': 74.3,
    'place_name': type,
    'address_line_1': '$type address',
    'address_line_2': null,
    'city': 'Lahore',
    'state': null,
    'country': 'Pakistan',
    'postal_code': null,
    'contact_name': null,
    'contact_phone': null,
    'instructions': null,
    'arrived_at': null,
    'completed_at': null,
  };
}
