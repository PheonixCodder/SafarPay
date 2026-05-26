import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../data/rides/ride_models.dart';
import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';
import 'ride_details_button.dart';
import 'ride_display_utils.dart';
import 'ride_highlight_row.dart';
import 'ride_route_summary.dart';
import 'ride_status_chip.dart';

class SRideCard extends StatelessWidget {
  const SRideCard({
    super.key,
    required this.ride,
    required this.accentColor,
    required this.statusText,
    required this.onPressed,
    this.highlightLabel,
    this.highlightValue,
    this.actionLabel = STexts.tripsViewDetails,
  });

  final RideSummaryResponse ride;
  final Color accentColor;
  final String statusText;
  final VoidCallback onPressed;
  final String? highlightLabel;
  final String? highlightValue;
  final String actionLabel;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: SColors.white,
      borderRadius: BorderRadius.circular(SSizes.tripsCardRadius),
      child: InkWell(
        borderRadius: BorderRadius.circular(SSizes.tripsCardRadius),
        onTap: onPressed,
        child: Container(
          padding: const EdgeInsets.all(SSizes.tripsCardPadding),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(SSizes.tripsCardRadius),
            border: Border.all(color: SColors.borderSecondary),
            boxShadow: [
              BoxShadow(
                color: SHelperFunctions.withOpacity(
                  SColors.pureBlack,
                  SOpacities.subtle,
                ),
                blurRadius: SSizes.shadowBlurLg,
                offset: const Offset(0, SSizes.shadowOffsetYMd),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 42,
                    height: 42,
                    decoration: BoxDecoration(
                      color: SHelperFunctions.withOpacity(
                        accentColor,
                        SOpacities.light,
                      ),
                      borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
                    ),
                    child: Icon(Iconsax.routing, color: accentColor),
                  ),
                  const SizedBox(width: SSizes.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          SRideDisplayUtils.summaryRouteTitle(ride),
                          style:
                              Theme.of(context).textTheme.titleMedium?.copyWith(
                                    color: SColors.textPrimary,
                                    fontWeight: FontWeight.w900,
                                  ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: SSizes.xs),
                        Text(
                          '${SRideDisplayUtils.service(ride.serviceType)} - '
                          '${SRideDisplayUtils.category(ride.category)} - '
                          '${SRideDisplayUtils.payment(ride.passengerPaymentMethod)}',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: SColors.textSecondary,
                                  ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: SSizes.sm),
                  SRideStatusChip(label: statusText, color: accentColor),
                ],
              ),
              const SizedBox(height: SSizes.md),
              SRideRouteSummary.fromStops(
                pickupStop: ride.pickupStop,
                dropoffStop: ride.dropoffStop,
              ),
              const SizedBox(height: SSizes.md),
              if (highlightLabel != null && highlightValue != null) ...[
                SRideHighlightRow(
                  label: highlightLabel!,
                  value: highlightValue!,
                ),
                const SizedBox(height: SSizes.md),
              ],
              Row(
                children: [
                  Expanded(
                    child: SRideHighlightRow(
                      label: STexts.tripsCreated,
                      value: SRideDisplayUtils.dateTime(ride.createdAt),
                    ),
                  ),
                  const SizedBox(width: SSizes.md),
                  SRideDetailsButton(
                    label: actionLabel,
                    onPressed: onPressed,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
