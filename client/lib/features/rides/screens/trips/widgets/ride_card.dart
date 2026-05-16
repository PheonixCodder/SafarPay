import 'package:flutter/material.dart';

import '../../../../../common/navigation/right_slide_page_route.dart';
import '../../../../../data/rides/ride_models.dart';
import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';
import '../screens/ride/ride.dart';
import 'ride_details_button.dart';
import 'ride_display_utils.dart';
import 'ride_route_summary.dart';

class SRideCard extends StatelessWidget {
  const SRideCard({
    super.key,
    required this.ride,
    required this.accentColor,
    required this.statusText,
    this.highlightLabel,
    this.highlightValue,
  });

  final RideResponse ride;
  final Color accentColor;
  final String statusText;
  final String? highlightLabel;
  final String? highlightValue;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(SSizes.tripsCardPadding),
      decoration: BoxDecoration(
        color: SColors.white,
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
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      SRideDisplayUtils.routeTitle(ride),
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: SColors.textPrimary,
                            fontWeight: FontWeight.w800,
                          ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: SSizes.xs),
                    Text(
                      '${SRideDisplayUtils.service(ride.serviceType)} • '
                      '${SRideDisplayUtils.category(ride.category)} • '
                      '${SRideDisplayUtils.payment(ride.passengerPaymentMethod)}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: SColors.textSecondary,
                          ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: SSizes.sm),
              _StatusChip(label: statusText, color: accentColor),
            ],
          ),
          const SizedBox(height: SSizes.md),
          SRideRouteSummary(ride: ride),
          const SizedBox(height: SSizes.md),
          if (highlightLabel != null && highlightValue != null) ...[
            _HighlightRow(label: highlightLabel!, value: highlightValue!),
            const SizedBox(height: SSizes.md),
          ],
          Row(
            children: [
              Expanded(
                child: _HighlightRow(
                  label: STexts.tripsPrice,
                  value: SRideDisplayUtils.money(ride.finalPrice),
                ),
              ),
              const SizedBox(width: SSizes.md),
              SRideDetailsButton(
                onPressed: () => Navigator.of(context).push(
                  SRightSlidePageRoute(page: RideDetailsScreen(ride: ride)),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  const _StatusChip({required this.label, required this.color});

  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: SSizes.sm,
        vertical: SSizes.xs,
      ),
      decoration: BoxDecoration(
        color: SHelperFunctions.withOpacity(color, SOpacities.placeholder),
        borderRadius: BorderRadius.circular(SSizes.tripsStatusChipRadius),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: color,
              fontWeight: FontWeight.w800,
            ),
      ),
    );
  }
}

class _HighlightRow extends StatelessWidget {
  const _HighlightRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: SColors.textSecondary,
                fontWeight: FontWeight.w700,
              ),
        ),
        const SizedBox(height: SSizes.xs),
        Text(
          value,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: SColors.textPrimary,
                fontWeight: FontWeight.w800,
              ),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    );
  }
}
