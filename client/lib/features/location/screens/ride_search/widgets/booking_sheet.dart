import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/domain/bidding_models.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/features/location/screens/ride_search/widgets/booking_category_strip.dart';
import 'package:client/features/location/screens/ride_search/widgets/booking_search_results.dart';
import 'package:client/features/location/screens/ride_search/widgets/fare_offer_panel.dart';
import 'package:client/features/location/screens/ride_search/widgets/location_input_bar.dart';
import 'package:client/features/location/screens/ride_search/widgets/vehicle_offer_list.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

class SBookingSheet extends StatelessWidget {
  const SBookingSheet({
    super.key,
    required this.controller,
    this.onAcceptedRideTrackingRequested,
  });

  final SRideSearchController controller;
  final ValueChanged<String>? onAcceptedRideTrackingRequested;

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.42,
      minChildSize: 0.20,
      maxChildSize: 0.88,
      snap: true,
      snapSizes: const [0.42, 0.68, 0.88],
      builder: (context, scrollController) {
        return DecoratedBox(
          decoration: const BoxDecoration(
            color: SColors.primaryBackground,
            borderRadius: BorderRadius.vertical(
              top: Radius.circular(SSizes.rideSheetRadius),
            ),
          ),
          child: ListView(
            controller: scrollController,
            padding: const EdgeInsets.fromLTRB(
              SSizes.defaultSpace,
              SSizes.sm,
              SSizes.defaultSpace,
              SSizes.defaultSpace,
            ),
            children: [
              Center(
                child: Container(
                  width: 44,
                  height: 5,
                  decoration: BoxDecoration(
                    color: SColors.borderPrimary,
                    borderRadius: BorderRadius.circular(SSizes.radiusFull),
                  ),
                ),
              ),
              const SizedBox(height: SSizes.md),
              Obx(
                () => _SheetContent(
                  controller: controller,
                  mode: controller.sheetMode.value,
                  onAcceptedRideTrackingRequested:
                      onAcceptedRideTrackingRequested,
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _SheetContent extends StatelessWidget {
  const _SheetContent({
    required this.controller,
    required this.mode,
    required this.onAcceptedRideTrackingRequested,
  });

  final SRideSearchController controller;
  final SBookingSheetMode mode;
  final ValueChanged<String>? onAcceptedRideTrackingRequested;

  @override
  Widget build(BuildContext context) {
    return switch (mode) {
      SBookingSheetMode.search => _SearchContent(controller: controller),
      SBookingSheetMode.vehicles => _VehicleContent(controller: controller),
      SBookingSheetMode.matching => _MatchingContent(
          controller: controller,
          onAcceptedRideTrackingRequested: onAcceptedRideTrackingRequested,
        ),
      _ => _ComposeContent(controller: controller),
    };
  }
}

class _ComposeContent extends StatelessWidget {
  const _ComposeContent({required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Obx(() {
      final pickup = controller.pickup.value;
      final dropoff = controller.selectedDropoff.value;
      final route = controller.route.value;
      final selectedCategory = controller.selectedCategory.value;
      final activeTarget = controller.activeTarget.value;
      final errorMessage = controller.errorMessage.value;

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Book your ride',
            style: textTheme.titleLarge?.copyWith(
              color: SColors.textPrimary,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: SSizes.md),
          SLocationInputBar(
            label: 'Pickup',
            value: pickup?.formatted ?? 'Search or use the map pin',
            target: SBookingLocationTarget.pickup,
            isActive: activeTarget == SBookingLocationTarget.pickup,
            onTap: () => controller.focusSearch(SBookingLocationTarget.pickup),
            onPinTap: () =>
                controller.startMapPinSelection(SBookingLocationTarget.pickup),
          ),
          const SizedBox(height: SSizes.sm),
          SLocationInputBar(
            label: 'Dropoff',
            value: dropoff?.formatted ?? 'Where to?',
            target: SBookingLocationTarget.dropoff,
            isActive: activeTarget == SBookingLocationTarget.dropoff,
            onTap: () => controller.focusSearch(SBookingLocationTarget.dropoff),
            onPinTap: () =>
                controller.startMapPinSelection(SBookingLocationTarget.dropoff),
          ),
          const SizedBox(height: SSizes.md),
          SBookingCategoryStrip(
            selectedCategory: selectedCategory,
            onSelected: controller.selectCategory,
          ),
          if (route != null) ...[
            const SizedBox(height: SSizes.md),
            _RouteSummary(
              distanceKm: route.distanceKm,
              durationMinutes: route.durationMinutes,
            ),
          ],
          if (errorMessage.isNotEmpty) ...[
            const SizedBox(height: SSizes.sm),
            Text(
              errorMessage,
              style: textTheme.bodySmall?.copyWith(color: SColors.error),
            ),
          ],
          const SizedBox(height: SSizes.md),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: controller.hasPickupAndDropoff
                  ? controller.showVehicleSelection
                  : null,
              icon: const Icon(Iconsax.car),
              label: Text(route == null ? 'Preview route' : 'Choose vehicle'),
            ),
          ),
        ],
      );
    });
  }
}

class _SearchContent extends StatelessWidget {
  const _SearchContent({required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    final isPickup =
        controller.activeTarget.value == SBookingLocationTarget.pickup;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        TextField(
          controller: isPickup
              ? controller.pickupSearchController
              : controller.dropoffSearchController,
          autofocus: true,
          textInputAction: TextInputAction.search,
          onChanged: controller.onSearchChanged,
          decoration: InputDecoration(
            hintText: isPickup ? 'Search pickup' : 'Where to?',
            prefixIcon: Icon(isPickup ? Iconsax.location_tick : Iconsax.flag),
            suffixIcon: IconButton(
              onPressed: () => controller.sheetMode.value =
                  SBookingSheetMode.compose,
              icon: const Icon(Iconsax.close_circle),
            ),
            filled: true,
            fillColor: SColors.white,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
              borderSide: const BorderSide(color: SColors.borderPrimary),
            ),
          ),
        ),
        const SizedBox(height: SSizes.md),
        SBookingSearchResults(
          isLoading: controller.isLoading.value,
          errorMessage: controller.errorMessage.value,
          results: controller.results,
          onSelected: controller.selectAddress,
        ),
      ],
    );
  }
}

class _VehicleContent extends StatelessWidget {
  const _VehicleContent({required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Obx(() {
      final selected = controller.selectedVehicle.value;
      final selectedCategory = controller.selectedCategory.value;
      final availableVehicles = controller.availableVehicles;
      final errorMessage = controller.errorMessage.value;
      final isCreatingRide = controller.isCreatingRide.value;

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              IconButton(
                onPressed: () =>
                    controller.sheetMode.value = SBookingSheetMode.route,
                icon: const Icon(Iconsax.arrow_left),
              ),
              Expanded(
                child: Text(
                  'Choose your ride',
                  style: textTheme.titleLarge?.copyWith(
                    color: SColors.textPrimary,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: SSizes.sm),
          SBookingCategoryStrip(
            selectedCategory: selectedCategory,
            onSelected: controller.selectCategory,
          ),
          const SizedBox(height: SSizes.md),
          SVehicleOfferList(
            offers: availableVehicles,
            selectedOffer: selected,
            onSelected: controller.selectVehicle,
          ),
          const SizedBox(height: SSizes.sm),
          SFareOfferPanel(controller: controller),
          if (errorMessage.isNotEmpty) ...[
            const SizedBox(height: SSizes.sm),
            Text(
              errorMessage,
              style: textTheme.bodySmall?.copyWith(color: SColors.error),
            ),
          ],
          const SizedBox(height: SSizes.md),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: isCreatingRide ? null : controller.createHybridRide,
              icon: isCreatingRide
                  ? const SizedBox(
                      width: SSizes.iconSm,
                      height: SSizes.iconSm,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Iconsax.send_2),
              label: Text(
                isCreatingRide ? 'Finding offers...' : 'Find offers',
              ),
            ),
          ),
        ],
      );
    });
  }
}

class _MatchingContent extends StatelessWidget {
  const _MatchingContent({
    required this.controller,
    required this.onAcceptedRideTrackingRequested,
  });

  final SRideSearchController controller;
  final ValueChanged<String>? onAcceptedRideTrackingRequested;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Obx(() {
      final hasSession = controller.biddingSessionId.value.isNotEmpty;
      final acceptedBid = controller.acceptedBid.value;
      final driverBids = controller.driverBids.toList();
      final isCreatingRide = controller.isCreatingRide.value;
      final passengerOffer = controller.passengerOffer.value;
      final createdRideId = controller.createdRideId.value;

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Finding driver offers',
            style: textTheme.titleLarge?.copyWith(
              color: SColors.textPrimary,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: SSizes.sm),
          Text(
            acceptedBid != null
                ? 'Offer accepted. Preparing ride tracking.'
                : hasSession
                    ? 'Live bidding session connected.'
                    : 'Ride created. Waiting for backend bidding session id.',
            style: textTheme.bodyMedium?.copyWith(
              color: SColors.textSecondary,
            ),
          ),
          const SizedBox(height: SSizes.md),
          LinearProgressIndicator(
            color: SColors.primary,
            backgroundColor: SColors.borderSecondary,
          ),
          const SizedBox(height: SSizes.md),
          Text(
            createdRideId.isEmpty ? 'No ride id returned yet.' : 'Ride $createdRideId',
            style: textTheme.bodySmall?.copyWith(color: SColors.textSecondary),
          ),
          if (driverBids.isNotEmpty) ...[
            const SizedBox(height: SSizes.md),
            for (final bid in driverBids)
              Padding(
                padding: const EdgeInsets.only(bottom: SSizes.sm),
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    color: SColors.white,
                    borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                    border: Border.all(color: SColors.borderSecondary),
                  ),
                  child: ListTile(
                    leading: const Icon(Iconsax.car, color: SColors.primary),
                    title: Text(
                      'PKR${bid.bidAmount.round()}',
                      style: textTheme.titleMedium?.copyWith(
                        color: SColors.textPrimary,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    subtitle: Text(
                      '${bid.etaMinutes ?? '-'} min pickup'
                      '${bid.message == null ? '' : ' - ${bid.message}'}',
                    ),
                    trailing: TextButton(
                      onPressed: isCreatingRide
                          ? null
                          : () => _acceptBid(bid),
                      child: const Text('Accept'),
                    ),
                  ),
                ),
              ),
          ],
          if (hasSession && acceptedBid == null) ...[
            const SizedBox(height: SSizes.md),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: controller.sendCounterOffer,
                icon: const Icon(Iconsax.refresh),
                label: Text(
                  'Send counter offer PKR${passengerOffer.round()}',
                ),
              ),
            ),
          ],
        ],
      );
    });
  }

  Future<void> _acceptBid(SBid bid) async {
    final accepted = await controller.acceptDriverBid(bid);
    if (!accepted) return;

    final rideId = controller.createdRideId.value;
    if (rideId.isEmpty) {
      controller.errorMessage.value =
          'Ride accepted, but tracking could not open without a ride id.';
      return;
    }

    onAcceptedRideTrackingRequested?.call(rideId);
  }
}

class _RouteSummary extends StatelessWidget {
  const _RouteSummary({
    required this.distanceKm,
    required this.durationMinutes,
  });

  final double distanceKm;
  final double durationMinutes;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Padding(
        padding: const EdgeInsets.all(SSizes.md),
        child: Row(
          children: [
            const Icon(Iconsax.route_square, color: SColors.primary),
            const SizedBox(width: SSizes.sm),
            Expanded(
              child: Text(
                '${distanceKm.toStringAsFixed(1)} km - ${durationMinutes.round()} min',
                style: textTheme.titleSmall?.copyWith(
                  color: SColors.textPrimary,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
