import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';

class SRideDetailsButton extends StatelessWidget {
  const SRideDetailsButton({
    super.key,
    required this.onPressed,
    this.label = STexts.tripsViewDetails,
  });

  final VoidCallback onPressed;
  final String label;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: SSizes.buttonWidth,
      height: SSizes.tripsDetailsButtonHeight,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: SColors.primary,
          foregroundColor: SColors.white,
          elevation: 0,
          minimumSize: const Size(
            SSizes.buttonWidth,
            SSizes.tripsDetailsButtonHeight,
          ),
          padding: const EdgeInsets.symmetric(horizontal: SSizes.sm),
          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
          textStyle: Theme.of(context).textTheme.labelLarge?.copyWith(
                fontWeight: FontWeight.w800,
              ),
          shape: RoundedRectangleBorder(
            borderRadius:
                BorderRadius.circular(SSizes.tripsDetailsButtonRadius),
          ),
        ),
        child: Text(
          label,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(color: SColors.white),
        ),
      ),
    );
  }
}
