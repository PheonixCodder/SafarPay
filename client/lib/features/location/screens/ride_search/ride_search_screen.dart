import 'package:client/common/widgets/maps/map_models.dart';
import 'package:client/common/widgets/maps/map_view.dart';
import 'package:client/common/navigation/right_slide_page_route.dart';
import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/features/location/screens/ride_search/widgets/booking_map_controls.dart';
import 'package:client/features/location/screens/ride_search/widgets/booking_sheet.dart';
import 'package:client/features/location/screens/ride_tracking/ride_tracking_screen.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class RideSearchScreen extends StatefulWidget {
  const RideSearchScreen({
    super.key,
    this.initialCategory = SPassengerServiceCategory.cityRides,
  });

  final SPassengerServiceCategory initialCategory;

  @override
  State<RideSearchScreen> createState() => _RideSearchScreenState();
}

class _RideSearchScreenState extends State<RideSearchScreen> {
  late final String _controllerTag;
  late final SRideSearchController _controller;

  @override
  void initState() {
    super.initState();
    _controllerTag =
        'ride-search-${widget.initialCategory.name}-${identityHashCode(this)}';
    _controller = Get.put(
      SRideSearchController(initialCategory: widget.initialCategory),
      tag: _controllerTag,
    );
  }

  @override
  void dispose() {
    if (Get.isRegistered<SRideSearchController>(tag: _controllerTag)) {
      Get.delete<SRideSearchController>(tag: _controllerTag, force: true);
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      body: Obx(
        () {
          final pickup = _controller.pickup.value;
          final dropoff = _controller.selectedDropoff.value;
          final hasRoute = _controller.route.value != null;

          return Stack(
            children: [
              Positioned.fill(
                child: SMapView(
                  controller: _controller.mapController,
                  initialCenter: _controller.mapCenter,
                  cameraMode: hasRoute
                      ? SMapCameraMode.fitRoute
                      : SMapCameraMode.manual,
                  fitPadding: const EdgeInsets.fromLTRB(48, 140, 48, 360),
                  fullBleed: true,
                  showStatusPill: false,
                  showRecenterButton: false,
                  showCenterPin: !hasRoute,
                  showUserLocation: false,
                  isLoading: _controller.isRouteLoading.value,
                  errorMessage: _controller.errorMessage.value.isEmpty
                      ? null
                      : _controller.errorMessage.value,
                  route: _controller.route.value,
                  markers: [
                    if (pickup != null)
                      SMapMarker(
                        id: 'pickup',
                        coordinate: pickup.coordinate,
                        type: SMapMarkerType.pickup,
                        label: 'Pickup',
                      ),
                    if (dropoff != null)
                      SMapMarker(
                        id: 'dropoff',
                        coordinate: dropoff.coordinate,
                        type: SMapMarkerType.dropoff,
                        label: 'Dropoff',
                      ),
                  ],
                ),
              ),
              Positioned(
                left: 0,
                right: 0,
                top: 0,
                child: SBookingMapControls(controller: _controller),
              ),
              SBookingSheet(
                controller: _controller,
                onAcceptedRideTrackingRequested: (rideId) {
                  Navigator.of(context).pushReplacement(
                    SRightSlidePageRoute(
                      page: RideTrackingScreen(rideId: rideId),
                    ),
                  );
                },
              ),
            ],
          );
        },
      ),
    );
  }
}
