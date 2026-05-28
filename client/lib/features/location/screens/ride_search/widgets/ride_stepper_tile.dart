import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';

class SRideStepperTile extends StatelessWidget {
  const SRideStepperTile({
    super.key,
    required this.label,
    required this.value,
    required this.onMinus,
    required this.onPlus,
  });

  final String label;
  final int value;
  final VoidCallback onMinus;
  final VoidCallback onPlus;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(
        horizontal: SSizes.sm,
        vertical: SSizes.xs,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(SSizes.cardRadiusSm),
        side: const BorderSide(color: SColors.borderSecondary),
      ),
      tileColor: SColors.lightContainer,
      title: Text(
        label,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: SColors.textPrimary,
              fontWeight: FontWeight.w700,
            ),
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton.filledTonal(
            onPressed: onMinus,
            icon: const Icon(Icons.remove),
          ),
          SizedBox(
            width: 36,
            child: Center(
              child: Text(
                '$value',
                style: const TextStyle(
                  color: SColors.textPrimary,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ),
          IconButton.filledTonal(
            onPressed: onPlus,
            icon: const Icon(Icons.add),
          ),
        ],
      ),
    );
  }
}
