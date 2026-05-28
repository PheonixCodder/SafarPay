import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../data/rides/ride_models.dart';
import '../../../../../../utils/constants/colors.dart';
import '../../../../../../utils/constants/sizes.dart';
import '../../../../../../utils/helpers/helpers.dart';
import '../../widgets/ride_display_utils.dart';
import '../../widgets/ride_route_summary.dart';

class FixedRideWaitingScreen extends StatelessWidget {
  const FixedRideWaitingScreen({
    super.key,
    required this.ride,
  });

  final RideSummaryResponse ride;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text('Finding driver'),
      ),
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: () async {},
          child: ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(SSizes.defaultSpace),
            children: [
              Container(
                padding: const EdgeInsets.all(SSizes.lg),
                decoration: BoxDecoration(
                  color: SColors.white,
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                  border: Border.all(color: SColors.borderSecondary),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 48,
                          height: 48,
                          decoration: BoxDecoration(
                            color: SHelperFunctions.withOpacity(
                              SColors.primary,
                              SOpacities.light,
                            ),
                            borderRadius:
                                BorderRadius.circular(SSizes.cardRadiusMd),
                          ),
                          child: const Icon(
                            Iconsax.car,
                            color: SColors.primary,
                          ),
                        ),
                        const SizedBox(width: SSizes.md),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Fixed ride request sent',
                                style: textTheme.titleMedium?.copyWith(
                                  color: SColors.textPrimary,
                                  fontWeight: FontWeight.w900,
                                ),
                              ),
                              Text(
                                'Drivers can accept this fare directly.',
                                style: textTheme.bodySmall?.copyWith(
                                  color: SColors.textSecondary,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: SSizes.lg),
                    SRideRouteSummary.fromStops(
                      pickupStop: ride.pickupStop,
                      dropoffStop: ride.dropoffStop,
                    ),
                    const SizedBox(height: SSizes.lg),
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(SSizes.md),
                      decoration: BoxDecoration(
                        color: SHelperFunctions.withOpacity(
                          SColors.primary,
                          SOpacities.placeholder,
                        ),
                        borderRadius:
                            BorderRadius.circular(SSizes.cardRadiusMd),
                      ),
                      child: Text(
                        'No bidding is needed for ${SRideDisplayUtils.pricing(ride.pricingMode).toLowerCase()} rides. We will open live tracking as soon as a driver accepts.',
                        style: textTheme.bodyMedium?.copyWith(
                          color: SColors.textPrimary,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                    const SizedBox(height: SSizes.md),
                    OutlinedButton.icon(
                      onPressed: () => Navigator.of(context).pop(),
                      icon: const Icon(Iconsax.arrow_left),
                      label: const Text('Back to trips'),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
