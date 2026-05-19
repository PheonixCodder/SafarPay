import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/helpers/helpers.dart';
import 'package:flutter/material.dart';

class SBookingCategoryStrip extends StatelessWidget {
  const SBookingCategoryStrip({
    super.key,
    required this.selectedCategory,
    required this.onSelected,
  });

  final SPassengerServiceCategory selectedCategory;
  final ValueChanged<SPassengerServiceCategory> onSelected;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 92,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: SRideBookingCatalog.services.length,
        separatorBuilder: (_, __) => const SizedBox(width: SSizes.sm),
        itemBuilder: (context, index) {
          final item = SRideBookingCatalog.services[index];
          final isSelected = item.category == selectedCategory;

          return _CategoryChip(
            item: item,
            isSelected: isSelected,
            onTap: () => onSelected(item.category),
          );
        },
      ),
    );
  }
}

class _CategoryChip extends StatelessWidget {
  const _CategoryChip({
    required this.item,
    required this.isSelected,
    required this.onTap,
  });

  final SRideServiceOption item;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return InkWell(
      borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        width: 132,
        padding: const EdgeInsets.all(SSizes.sm),
        decoration: BoxDecoration(
          color: isSelected ? SColors.primary : SColors.lightContainer,
          borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
          border: Border.all(
            color: isSelected ? SColors.primary : SColors.borderSecondary,
          ),
        ),
        child: Row(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
              child: Image.asset(
                item.image,
                width: 44,
                height: 44,
                fit: BoxFit.contain,
                errorBuilder: (_, __, ___) => const Icon(Icons.directions_car),
              ),
            ),
            const SizedBox(width: SSizes.sm),
            Expanded(
              child: Text(
                item.title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: textTheme.labelLarge?.copyWith(
                  color: isSelected ? SColors.textWhite : SColors.textPrimary,
                  fontWeight: FontWeight.w800,
                  height: 1.1,
                ),
              ),
            ),
            if (!item.isBookable)
              Container(
                width: SSizes.xs,
                height: SSizes.xs,
                decoration: BoxDecoration(
                  color: SHelperFunctions.withOpacity(
                    isSelected ? SColors.white : SColors.warning,
                    SOpacities.strong,
                  ),
                  borderRadius: BorderRadius.circular(SSizes.radiusFull),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
