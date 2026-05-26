import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../domain/earnings_models.dart';

class SEarningsWithdrawButton extends StatelessWidget {
  const SEarningsWithdrawButton({super.key, required this.earnings});

  final SDriverEarnings earnings;

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: earnings.withdrawUnavailableReason ?? '',
      child: SizedBox(
        height: 56,
        child: ElevatedButton(
          onPressed: earnings.withdrawAvailable ? () {} : null,
          style: ElevatedButton.styleFrom(
            backgroundColor: SColors.primary,
            disabledBackgroundColor: SColors.buttonDisabled,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(SSizes.borderRadiusMd),
            ),
          ),
          child: Text(
            STexts.earningsWithdraw,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: SColors.white,
                  fontWeight: FontWeight.w800,
                ),
          ),
        ),
      ),
    );
  }
}
