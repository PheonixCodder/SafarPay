import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';

class SDriverRegistrationErrorText extends StatelessWidget {
  const SDriverRegistrationErrorText({
    super.key,
    this.message,
  });

  final String? message;

  @override
  Widget build(BuildContext context) {
    if (message == null) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(top: SSizes.md),
      child: Text(
        message!,
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: SColors.error,
              fontWeight: FontWeight.w700,
            ),
      ),
    );
  }
}
