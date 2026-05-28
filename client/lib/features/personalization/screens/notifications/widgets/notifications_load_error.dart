import 'package:flutter/material.dart';

import '../../../../../utils/constants/sizes.dart';

class SNotificationsLoadError extends StatelessWidget {
  const SNotificationsLoadError({
    super.key,
    required this.message,
    required this.onRetry,
  });

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: SSizes.spaceBtwSections),
      child: Column(
        children: [
          Text(
            message,
            style: Theme.of(context).textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: SSizes.sm),
          OutlinedButton(
            onPressed: onRetry,
            child: const Text('Try again'),
          ),
        ],
      ),
    );
  }
}
