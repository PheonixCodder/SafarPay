import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

class SDriverRegistrationDateField extends StatelessWidget {
  const SDriverRegistrationDateField({
    super.key,
    required this.label,
    required this.value,
    required this.error,
    required this.onTap,
  });

  final String label;
  final DateTime? value;
  final String? error;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final text = value == null
        ? STexts.driverRegistrationSelectDate
        : '${value!.year}-${value!.month.toString().padLeft(2, '0')}-${value!.day.toString().padLeft(2, '0')}';

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(SSizes.inputFieldRadius),
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: label,
          errorText: error,
          prefixIcon: const Icon(Iconsax.calendar),
        ),
        child: Text(text),
      ),
    );
  }
}
