import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';
import '../../../domain/earnings_models.dart';

class SEarningsPeriodMenu extends StatelessWidget {
  const SEarningsPeriodMenu({
    super.key,
    required this.selected,
    required this.onSelected,
  });

  final SDriverEarningsPeriod selected;
  final ValueChanged<SDriverEarningsPeriod> onSelected;

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<SDriverEarningsPeriod>(
      onSelected: onSelected,
      itemBuilder: (context) => SDriverEarningsPeriod.values
          .map(
            (period) => PopupMenuItem(
              value: period,
              child: Text(period.label),
            ),
          )
          .toList(),
      child: Container(
        padding: const EdgeInsets.symmetric(
          horizontal: SSizes.md,
          vertical: SSizes.sm,
        ),
        decoration: BoxDecoration(
          color: SColors.white,
          borderRadius: BorderRadius.circular(SSizes.borderRadiusMd),
          border: Border.all(
            color: SHelperFunctions.withOpacity(
              SColors.borderPrimary,
              SOpacities.strong,
            ),
          ),
        ),
        child: Row(
          children: [
            Text(
              selected.label,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: SColors.primary,
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(width: SSizes.xs),
            const Icon(Iconsax.arrow_down_1, color: SColors.primary, size: 16),
          ],
        ),
      ),
    );
  }
}
