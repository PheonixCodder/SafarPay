import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';
import '../../../domain/earnings_models.dart';
import 'earnings_formatters.dart';

class SEarningsSummaryCard extends StatelessWidget {
  const SEarningsSummaryCard({super.key, required this.earnings});

  final SDriverEarnings earnings;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(SSizes.lg),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.borderRadiusMd),
        border: Border.all(color: SColors.borderSecondary),
        boxShadow: [
          BoxShadow(
            color: SHelperFunctions.withOpacity(
              SColors.pureBlack,
              SOpacities.soft,
            ),
            blurRadius: SSizes.shadowBlurLg,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  STexts.earningsNet,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: SColors.textSecondary,
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: SSizes.sm),
                FittedBox(
                  alignment: Alignment.centerLeft,
                  fit: BoxFit.scaleDown,
                  child: Text(
                    sFormatMoney(
                      earnings.summary.netEarnings,
                      currency: earnings.currency,
                    ),
                    style: Theme.of(context).textTheme.displaySmall?.copyWith(
                          color: SColors.black,
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: SSizes.md),
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              color: SHelperFunctions.withOpacity(
                SColors.primary,
                SOpacities.tinted,
              ),
              borderRadius: BorderRadius.circular(SSizes.borderRadiusMd),
            ),
            child: const Icon(
              Iconsax.wallet_3,
              color: SColors.primary,
              size: SSizes.iconLg,
            ),
          ),
        ],
      ),
    );
  }
}
