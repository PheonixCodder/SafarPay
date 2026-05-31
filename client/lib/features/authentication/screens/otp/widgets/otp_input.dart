import 'package:flutter/material.dart';
import 'package:pinput/pinput.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../controllers/otp.dart';

class SOtpInput extends StatelessWidget {
  const SOtpInput({
    super.key,
    required this.controller,
  });

  final SOtpController controller;

  @override
  Widget build(BuildContext context) {
    const double boxSize = 52.0;
    const double boxRadius = 14.0;

    final textStyle = Theme.of(context).textTheme.headlineSmall?.copyWith(
              color: SColors.textPrimary,
              fontWeight: FontWeight.w600,
              fontSize: SSizes.fontSizeXl,
            ) ??
        const TextStyle(
          color: SColors.textPrimary,
          fontWeight: FontWeight.w600,
          fontSize: SSizes.fontSizeXl,
        );

    final submittedTextStyle =
        Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: SColors.white,
                  fontWeight: FontWeight.w600,
                  fontSize: SSizes.fontSizeXl,
                ) ??
            const TextStyle(
              color: SColors.white,
              fontWeight: FontWeight.w600,
              fontSize: SSizes.fontSizeXl,
            );

    final defaultTheme = PinTheme(
      width: boxSize,
      height: boxSize,
      textStyle: textStyle,
      decoration: BoxDecoration(
        color: SColors.light,
        borderRadius: BorderRadius.circular(boxRadius),
      ),
    );

    final focusedTheme = defaultTheme.copyWith(
      textStyle: textStyle,
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(boxRadius),
        border: Border.all(
          color: SColors.textPrimary,
          width: 1.8,
        ),
        boxShadow: [
          BoxShadow(
            color: SColors.black.withValues(alpha: 0.08),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
    );

    final submittedTheme = PinTheme(
      width: boxSize,
      height: boxSize,
      textStyle: submittedTextStyle,
      decoration: BoxDecoration(
        color: SColors.textPrimary,
        borderRadius: BorderRadius.circular(boxRadius),
      ),
    );

    return Pinput(
      length: SOtpController.otpLength,
      defaultPinTheme: defaultTheme,
      focusedPinTheme: focusedTheme,
      submittedPinTheme: submittedTheme,
      autofocus: true,
      keyboardType: TextInputType.number,
      mainAxisAlignment: MainAxisAlignment.start,
      crossAxisAlignment: CrossAxisAlignment.center,
      separatorBuilder: (_) => const SizedBox(width: SSizes.sm),
      onChanged: controller.updateCode,
      onCompleted: controller.verifyOtp,
    );
  }
}
