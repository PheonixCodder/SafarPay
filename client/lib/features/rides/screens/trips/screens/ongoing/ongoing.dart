import 'package:flutter/material.dart';

import '../../../../../../data/rides/ride_models.dart';
import '../../../../controllers/trips_controller.dart';
import '../../widgets/trips_list.dart';

class OngoingTripsScreen extends StatelessWidget {
  const OngoingTripsScreen({
    super.key,
    required this.rides,
  });

  final List<RideSummaryResponse> rides;

  @override
  Widget build(BuildContext context) {
    return STripsList(
      filter: STripsFilter.ongoing,
      rides: rides,
    );
  }
}
