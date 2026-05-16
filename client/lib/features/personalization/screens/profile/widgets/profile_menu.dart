import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';

class SProfileMenu extends StatelessWidget {
  const SProfileMenu({
    super.key,
    required this.onPressed,
    required this.title,
    required this.value,
    this.icon = Iconsax.edit,
  });

  final IconData icon;
  final VoidCallback onPressed;
  final String title, value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(
        vertical: SSizes.profileMenuVerticalPadding,
      ),
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Text(
              title,
              style: Theme.of(context).textTheme.bodySmall,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          Expanded(
            flex: 5,
            child: Text(
              value,
              style: Theme.of(context).textTheme.bodyMedium,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          SizedBox.square(
            dimension: SSizes.profileEditIconBoxSize,
            child: Material(
              color: SHelperFunctions.withOpacity(
                SColors.primary,
                SOpacities.placeholder,
              ),
              borderRadius: BorderRadius.circular(
                SSizes.profileEditIconRadius,
              ),
              child: InkWell(
                onTap: onPressed,
                borderRadius: BorderRadius.circular(
                  SSizes.profileEditIconRadius,
                ),
                child: Icon(
                  icon,
                  size: SSizes.profileEditIconSize,
                  color: SColors.primary,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
