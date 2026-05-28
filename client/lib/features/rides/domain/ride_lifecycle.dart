import '../../../data/rides/ride_models.dart';

enum SRideLifecycleStage {
  scheduled,
  matchingForDriver,
  waitingForDriverAssignment,
  driverAssigned,
  driverEnRouteToPickup,
  driverArrivedAtPickup,
  tripInProgress,
  completed,
  cancelled,
  unknown,
}

class SRideLifecycleSnapshot {
  const SRideLifecycleSnapshot({
    required this.rideId,
    required this.pricingMode,
    required this.status,
    this.assignedDriverId,
    this.scheduledAt,
    this.pickupArrivedAt,
    this.hasExplicitPricingMode = true,
  });

  final String rideId;
  final PricingMode pricingMode;
  final RideStatus status;
  final String? assignedDriverId;
  final DateTime? scheduledAt;
  final DateTime? pickupArrivedAt;
  final bool hasExplicitPricingMode;

  bool get hasAssignedDriver {
    final value = assignedDriverId?.trim();
    return value != null && value.isNotEmpty;
  }

  bool get isHybrid => pricingMode == PricingMode.hybrid;

  bool get isBidDriven =>
      pricingMode == PricingMode.hybrid ||
      pricingMode == PricingMode.bidBased;

  SRideLifecycleStage get stage {
    if (scheduledAt != null && status == RideStatus.created) {
      return SRideLifecycleStage.scheduled;
    }
    if (pickupArrivedAt != null && status != RideStatus.completed) {
      if (status == RideStatus.inProgress) {
        return SRideLifecycleStage.tripInProgress;
      }
      return SRideLifecycleStage.driverArrivedAtPickup;
    }
    return switch (status) {
      RideStatus.created || RideStatus.matching => !hasAssignedDriver
          ? (isBidDriven
                ? SRideLifecycleStage.matchingForDriver
                : SRideLifecycleStage.waitingForDriverAssignment)
          : SRideLifecycleStage.driverAssigned,
      RideStatus.accepted => SRideLifecycleStage.driverAssigned,
      RideStatus.arriving => SRideLifecycleStage.driverEnRouteToPickup,
      RideStatus.inProgress => SRideLifecycleStage.tripInProgress,
      RideStatus.completed => SRideLifecycleStage.completed,
      RideStatus.cancelled => SRideLifecycleStage.cancelled,
    };
  }

  SRideLifecycleSnapshot copyWith({
    PricingMode? pricingMode,
    RideStatus? status,
    String? assignedDriverId,
    DateTime? scheduledAt,
    DateTime? pickupArrivedAt,
    bool? hasExplicitPricingMode,
  }) {
    return SRideLifecycleSnapshot(
      rideId: rideId,
      pricingMode: pricingMode ?? this.pricingMode,
      status: status ?? this.status,
      assignedDriverId: assignedDriverId ?? this.assignedDriverId,
      scheduledAt: scheduledAt ?? this.scheduledAt,
      pickupArrivedAt: pickupArrivedAt ?? this.pickupArrivedAt,
      hasExplicitPricingMode:
          hasExplicitPricingMode ?? this.hasExplicitPricingMode,
    );
  }

  factory SRideLifecycleSnapshot.fromSummary(RideSummaryResponse ride) {
    return SRideLifecycleSnapshot(
      rideId: ride.id,
      pricingMode: ride.pricingMode,
      status: ride.status,
      assignedDriverId: ride.assignedDriverId,
      scheduledAt: ride.scheduledAt,
      pickupArrivedAt: ride.pickupStop?.arrivedAt,
      hasExplicitPricingMode: ride.hasExplicitPricingMode,
    );
  }

  factory SRideLifecycleSnapshot.fromRide(RideResponse ride) {
    return SRideLifecycleSnapshot(
      rideId: ride.id,
      pricingMode: ride.pricingMode,
      status: ride.status,
      assignedDriverId: ride.assignedDriverId,
      scheduledAt: ride.scheduledAt,
      pickupArrivedAt: ride.pickupStop?.arrivedAt,
    );
  }

  factory SRideLifecycleSnapshot.fromDriverState({
    required String rideId,
    required String pricingMode,
    required String status,
    DateTime? pickupArrivedAt,
    String? assignedDriverId,
  }) {
    return SRideLifecycleSnapshot(
      rideId: rideId,
      pricingMode: _pricingModeFromRaw(pricingMode),
      status: _rideStatusFromRaw(status),
      assignedDriverId:
          assignedDriverId == null || assignedDriverId.trim().isEmpty
              ? 'driver'
              : assignedDriverId,
      pickupArrivedAt: pickupArrivedAt,
    );
  }
}

PricingMode _pricingModeFromRaw(String value) {
  for (final mode in PricingMode.values) {
    if (mode.value == value) return mode;
  }
  return PricingMode.fixed;
}

RideStatus _rideStatusFromRaw(String value) {
  for (final status in RideStatus.values) {
    if (status.value == value) return status;
  }
  return RideStatus.created;
}
