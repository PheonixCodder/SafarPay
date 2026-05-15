import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';

class SSettingsSectionHeading extends StatelessWidget {
  const SSettingsSectionHeading({
    super.key,
    required this.title,
  });

  final String title;

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleLarge?.copyWith(
              color: SColors.textPrimary,
              fontWeight: FontWeight.w700,
            ),
      ),
    );
  }
}
