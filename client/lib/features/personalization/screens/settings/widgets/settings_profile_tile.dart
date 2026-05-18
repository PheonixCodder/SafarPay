import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../common/widgets/images/circular_image.dart';
import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/images.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../../../../../utils/helpers/helpers.dart';

class SSettingsProfileTile extends StatelessWidget {
  const SSettingsProfileTile({
    super.key,
    this.onEdit,
  });

  final VoidCallback? onEdit;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Container(
      padding: const EdgeInsets.all(SSizes.lg),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(
          color: SHelperFunctions.withOpacity(SColors.grey, 0.15),
        ),
      ),
      child: Stack(
        children: [
          /// Main Content
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              /// Profile Image
              const SCircularImage(
                width: 90,
                height: 90,
                imageUrl: SImages.user,
              ),

              const SizedBox(height: SSizes.spaceBtwItems),

              /// Name
              Text(
                STexts.settingsProfileName,
                textAlign: TextAlign.center,
                style: textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),

              const SizedBox(height: 6),

              /// Email
              Text(
                STexts.settingsProfileEmail,
                textAlign: TextAlign.center,
                style: textTheme.bodyMedium?.copyWith(),
              ),
            ],
          ),

          /// Edit Button
          Positioned(
            bottom: 55,
            right: 4,
            child: Material(
              color: SHelperFunctions.withOpacity(SColors.primary, 0.12),
              borderRadius: BorderRadius.circular(14),
              child: InkWell(
                borderRadius: BorderRadius.circular(14),
                onTap: onEdit,
                child: const Padding(
                  padding: EdgeInsets.all(10),
                  child: Icon(
                    Iconsax.edit,
                    size: 18,
                    color: SColors.primary,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
