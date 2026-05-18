import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/texts.dart';

class SSettingsLogoutButton extends StatelessWidget {
  const SSettingsLogoutButton({
    super.key,
    this.onPressed,
  });

  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: OutlinedButton(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          side: const BorderSide(color: SColors.error),
        ),
        child: const Text(
          STexts.logout,
          style: TextStyle(color: SColors.error),
        ),
      ),
    );
  }
}
