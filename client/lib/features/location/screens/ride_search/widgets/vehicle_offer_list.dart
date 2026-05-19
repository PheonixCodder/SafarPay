import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/helpers/helpers.dart';
import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

class SVehicleOfferList extends StatelessWidget {
  const SVehicleOfferList({
    super.key,
    required this.offers,
    required this.selectedOffer,
    required this.onSelected,
  });

  final List<SRideVehicleOffer> offers;
  final SRideVehicleOffer? selectedOffer;
  final ValueChanged<SRideVehicleOffer> onSelected;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (final offer in offers)
          _VehicleOfferTile(
            offer: offer,
            isSelected: offer.id == selectedOffer?.id,
            onTap: () => onSelected(offer),
          ),
      ],
    );
  }
}

class _VehicleOfferTile extends StatelessWidget {
  const _VehicleOfferTile({
    required this.offer,
    required this.isSelected,
    required this.onTap,
  });

  final SRideVehicleOffer offer;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Padding(
      padding: const EdgeInsets.only(bottom: SSizes.sm),
      child: InkWell(
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          padding: const EdgeInsets.all(SSizes.md),
          decoration: BoxDecoration(
            color: isSelected
                ? SHelperFunctions.withOpacity(SColors.primary, 0.09)
                : SColors.white,
            borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
            border: Border.all(
              color: isSelected ? SColors.primary : SColors.borderSecondary,
              width: isSelected ? 1.6 : 1,
            ),
          ),
          child: Row(
            children: [
              Image.asset(
                offer.image,
                width: 58,
                height: 46,
                fit: BoxFit.contain,
                errorBuilder: (_, __, ___) => const Icon(Iconsax.car),
              ),
              const SizedBox(width: SSizes.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      offer.title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: textTheme.titleMedium?.copyWith(
                        color: SColors.textPrimary,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    const SizedBox(height: SSizes.xs),
                    Text(
                      '${offer.passengerCapacity} seat - ${offer.subtitle}',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: textTheme.bodySmall?.copyWith(
                        color: SColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: SSizes.sm),
              Text(
                '~PKR${offer.baseFare.round()}',
                style: textTheme.titleSmall?.copyWith(
                  color: SColors.textPrimary,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
