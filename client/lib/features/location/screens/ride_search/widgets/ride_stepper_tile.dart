import 'package:client/utils/constants/colors.dart';
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
      contentPadding: EdgeInsets.zero,
      title: Text(label),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          IconButton(onPressed: onMinus, icon: const Icon(Icons.remove)),
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
          IconButton(onPressed: onPlus, icon: const Icon(Icons.add)),
        ],
      ),
    );
  }
}
