import 'package:flutter/material.dart';

import '../../../../../common/navigation/right_slide_page_route.dart';
import '../../../../../data/rides/ride_models.dart';
import '../../../../../features/location/screens/ride_tracking/ride_tracking_screen.dart';
import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../controllers/trips_controller.dart';
import '../screens/pending/pending_ride_matching_screen.dart';
import '../screens/ride/ride.dart';
import 'ride_card.dart';
import 'ride_display_utils.dart';
import 'trips_empty_state.dart';

class STripsList extends StatelessWidget {
  const STripsList({
    super.key,
    required this.filter,
    required this.rides,
  });

  final STripsFilter filter;
  final List<RideSummaryResponse> rides;

  @override
  Widget build(BuildContext context) {
    if (rides.isEmpty) {
      return STripsEmptyState(title: _emptyTitle);
    }

    return ListView.separated(
      padding: EdgeInsets.zero,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: rides.length,
      separatorBuilder: (context, index) =>
          const SizedBox(height: SSizes.spaceBtnItems),
      itemBuilder: (context, index) {
        final ride = rides[index];
        return SRideCard(
          ride: ride,
          accentColor: _accentColor,
          statusText: _statusText(ride),
          highlightLabel: _highlightLabel,
          highlightValue: _highlightValue(ride),
          actionLabel: _actionLabel(ride),
          onPressed: () => _openRide(context, ride),
        );
      },
    );
  }

  String get _emptyTitle {
    return switch (filter) {
      STripsFilter.ongoing => STexts.tripsNoOngoing,
      STripsFilter.scheduled => STexts.tripsNoScheduled,
      STripsFilter.canceled => STexts.tripsNoCanceled,
      STripsFilter.completed => STexts.tripsNoCompleted,
    };
  }

  Color get _accentColor {
    return switch (filter) {
      STripsFilter.ongoing => SColors.primary,
      STripsFilter.scheduled => SColors.info,
      STripsFilter.canceled => SColors.error,
      STripsFilter.completed => SColors.success,
    };
  }

  String get _highlightLabel {
    return switch (filter) {
      STripsFilter.ongoing => STexts.tripsDriverAssigned,
      STripsFilter.scheduled => STexts.tripsScheduledFor,
      STripsFilter.canceled => STexts.tripsCanceledAt,
      STripsFilter.completed => STexts.tripsCompletedAt,
    };
  }

  String _statusText(RideSummaryResponse ride) {
    if (filter == STripsFilter.scheduled) return STexts.tripsScheduled;
    return SRideDisplayUtils.status(ride.status);
  }

  String _highlightValue(RideSummaryResponse ride) {
    return switch (filter) {
      STripsFilter.ongoing => ride.assignedDriverId == null
          ? STexts.tripsDriverPending
          : SRideDisplayUtils.dateTime(ride.createdAt),
      STripsFilter.scheduled => SRideDisplayUtils.dateTime(ride.scheduledAt),
      STripsFilter.canceled => SRideDisplayUtils.dateTime(ride.createdAt),
      STripsFilter.completed => SRideDisplayUtils.dateTime(ride.createdAt),
    };
  }

  String _actionLabel(RideSummaryResponse ride) {
    if (filter != STripsFilter.ongoing) return STexts.tripsViewDetails;
    return _shouldOpenTracking(ride) ? 'Track ride' : 'Finding driver';
  }

  void _openRide(BuildContext context, RideSummaryResponse ride) {
    if (filter == STripsFilter.ongoing) {
      if (!_shouldOpenTracking(ride)) {
        Navigator.of(context).push(
          SRightSlidePageRoute(
            page: PendingRideMatchingScreen(rideId: ride.id),
          ),
        );
        return;
      }
      Navigator.of(context).push(
        SRightSlidePageRoute(page: RideTrackingScreen(rideId: ride.id)),
      );
      return;
    }
    Navigator.of(context).push(
      SRightSlidePageRoute(page: RideDetailsScreen(rideId: ride.id)),
    );
  }

  bool _shouldOpenTracking(RideSummaryResponse ride) {
    if (ride.assignedDriverId == null || ride.assignedDriverId!.isEmpty) {
      return false;
    }
    return switch (ride.status) {
      RideStatus.accepted ||
      RideStatus.arriving ||
      RideStatus.inProgress =>
        true,
      RideStatus.created ||
      RideStatus.matching ||
      RideStatus.completed ||
      RideStatus.cancelled =>
        false,
    };
  }
}
