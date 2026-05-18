import 'package:client/common/widgets/appbar/appbar.dart';
import 'package:client/common/widgets/ride/search_result.dart';
import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/features/location/screens/ride_preview/ride_preview_screen.dart';
import 'package:client/features/location/screens/ride_search/widgets/pickup_card.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:client/utils/helpers/helpers.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

class RideSearchScreen extends StatelessWidget {
  const RideSearchScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(SRideSearchController());

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        showBackArrow: true,
        title: Text(
          STexts.rideSearchTitle,
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          children: [
            Text(
              STexts.rideSearchSubTitle,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: SColors.textSecondary,
                  ),
            ),
            const SizedBox(height: SSizes.lg),
            Obx(
              () => SPickupCard(
                label: controller.pickup.value?.formatted ??
                    STexts.rideSearchUseSearchPickup,
              ),
            ),
            const SizedBox(height: SSizes.md),
            TextField(
              controller: controller.queryController,
              onChanged: controller.onQueryChanged,
              textInputAction: TextInputAction.search,
              decoration: InputDecoration(
                hintText: STexts.rideSearchDropoffHint,
                prefixIcon: const Icon(Iconsax.search_normal),
                filled: true,
                fillColor: SColors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
                  borderSide: const BorderSide(color: SColors.borderPrimary),
                ),
              ),
            ),
            const SizedBox(height: SSizes.md),
            Obx(() {
              if (controller.isLoading.value) {
                return const Center(child: CircularProgressIndicator());
              }

              if (controller.results.isEmpty) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: SSizes.lg),
                  child: Text(
                    controller.errorMessage.value.isEmpty
                        ? STexts.rideSearchNoResults
                        : controller.errorMessage.value,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: SColors.textSecondary,
                        ),
                  ),
                );
              }

              return Column(
                children: controller.results.map((result) {
                  return SSearchResult(
                    icon: Iconsax.location,
                    title: result.formatted,
                    address: [
                      if (result.city != null) result.city,
                      if (result.country != null) result.country,
                    ].whereType<String>().join(', '),
                    duration: 'Route',
                    onTap: () {
                      controller.selectDropoff(result);
                      final pickup = controller.pickup.value;
                      if (pickup == null) {
                        SHelperFunctions.showSnackBar(
                          STexts.rideSearchUseSearchPickup,
                        );
                        return;
                      }
                      Get.to(
                        () => RidePreviewScreen(
                          pickup: pickup,
                          dropoff: result,
                        ),
                      );
                    },
                  );
                }).toList(),
              );
            }),
          ],
        ),
      ),
    );
  }
}
