import 'package:client/common/widgets/ride/recent_ride_destinations.dart';
import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/features/location/screens/ride_search/widgets/booking_category_strip.dart';
import 'package:client/features/location/screens/ride_search/widgets/booking_search_results.dart';
import 'package:client/features/location/screens/ride_search/widgets/fare_offer_panel.dart';
import 'package:client/features/location/screens/ride_search/widgets/location_input_bar.dart';
import 'package:client/features/location/screens/ride_search/widgets/matching_ride_offers_content.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_option_stepper.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_details_content.dart';
import 'package:client/features/location/screens/ride_search/widgets/ride_review_summary.dart';
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
      SBookingSheetMode.details => SRideDetailsContent(controller: controller),
      SBookingSheetMode.review => _ReviewContent(
          controller: controller,
          onAcceptedRideTrackingRequested: onAcceptedRideTrackingRequested,
        ),
      SBookingSheetMode.matching => SMatchingRideOffersContent(
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
            value: pickup?.displayLabel ?? 'Search or use the map pin',
            target: SBookingLocationTarget.pickup,
            isActive: activeTarget == SBookingLocationTarget.pickup,
            onTap: () => controller.focusSearch(SBookingLocationTarget.pickup),
            onPinTap: () =>
                controller.startMapPinSelection(SBookingLocationTarget.pickup),
          ),
          const SizedBox(height: SSizes.sm),
          SLocationInputBar(
            label: 'Dropoff',
            value: dropoff?.displayLabel ?? 'Where to?',
            target: SBookingLocationTarget.dropoff,
            isActive: activeTarget == SBookingLocationTarget.dropoff,
            onTap: () => controller.focusSearch(SBookingLocationTarget.dropoff),
            onPinTap: () =>
                controller.startMapPinSelection(SBookingLocationTarget.dropoff),
          ),
          const SizedBox(height: SSizes.md),
          SRecentRideDestinations(
            origin: pickup?.coordinate,
            onSelected: controller.selectRecentDropoff,
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
              onPressed: () =>
                  controller.sheetMode.value = SBookingSheetMode.compose,
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
        Obx(
          () => SBookingSearchResults(
            isLoading: controller.isLoading.value,
            errorMessage: controller.errorMessage.value,
            results: controller.results,
            onSelected: controller.selectAddress,
          ),
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
          const SRideOptionStepper(mode: SBookingSheetMode.vehicles),
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
              onPressed: isCreatingRide ? null : controller.showRideDetails,
              icon: const Icon(Iconsax.arrow_right_3),
              label: const Text('Next'),
            ),
          ),
        ],
      );
    });
  }
}

class _ReviewContent extends StatelessWidget {
  const _ReviewContent({
    required this.controller,
    required this.onAcceptedRideTrackingRequested,
  });

  final SRideSearchController controller;
  final ValueChanged<String>? onAcceptedRideTrackingRequested;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Obx(() {
      final isCreatingRide = controller.isCreatingRide.value;
      final createdRideId = controller.createdRideId.value;
      final errorMessage = controller.errorMessage.value;
      final isHybrid = controller.pricingMode.value.name == 'hybrid';

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              IconButton(
                onPressed: () =>
                    controller.sheetMode.value = SBookingSheetMode.details,
                icon: const Icon(Iconsax.arrow_left),
              ),
              Expanded(
                child: Text(
                  'Confirm booking',
                  style: textTheme.titleLarge?.copyWith(
                    color: SColors.textPrimary,
                    fontWeight: FontWeight.w900,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: SSizes.sm),
          const SRideOptionStepper(mode: SBookingSheetMode.review),
          const SizedBox(height: SSizes.md),
          SRideReviewSummary(controller: controller),
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
              onPressed: isCreatingRide || createdRideId.isNotEmpty
                  ? null
                  : controller.createRideFromDraft,
              icon: isCreatingRide
                  ? const SizedBox(
                      width: SSizes.iconSm,
                      height: SSizes.iconSm,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Icon(isHybrid ? Iconsax.send_2 : Iconsax.car),
              label: Text(
                isCreatingRide
                    ? 'Creating ride...'
                    : isHybrid
                        ? 'Find offers'
                        : 'Book fixed ride',
              ),
            ),
          ),
          if (createdRideId.isNotEmpty && !isHybrid) ...[
            const SizedBox(height: SSizes.sm),
            DecoratedBox(
              decoration: BoxDecoration(
                color: SColors.white,
                borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
                border: Border.all(color: SColors.borderSecondary),
              ),
              child: Padding(
                padding: const EdgeInsets.all(SSizes.md),
                child: Text(
                  'Fixed ride request sent. We will open live tracking after a driver accepts.',
                  style: textTheme.bodyMedium?.copyWith(
                    color: SColors.textSecondary,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ),
          ],
        ],
      );
    });
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
