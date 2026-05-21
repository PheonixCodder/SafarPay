import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../common/widgets/images/circular_image.dart';
import '../../../../authentication/controllers/current_user_controller.dart';
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
    final controller = SCurrentUserController.instance;

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
          Obx(
            () {
              final user = controller.currentUser.value;
              final profileImage = user?.profileImage;
              final hasNetworkImage =
                  profileImage != null && profileImage.startsWith('http');

              return Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SCircularImage(
                    width: 90,
                    height: 90,
                    imageUrl: profileImage ?? SImages.user,
                    isNetworkImage: hasNetworkImage,
                  ),
                  const SizedBox(height: SSizes.spaceBtwItems),
                  Text(
                    user?.fullName?.isNotEmpty == true
                        ? user!.fullName!
                        : STexts.currentUserFallbackName,
                    textAlign: TextAlign.center,
                    style: textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    user?.email?.isNotEmpty == true
                        ? user!.email!
                        : STexts.currentUserNoEmail,
                    textAlign: TextAlign.center,
                    style: textTheme.bodyMedium?.copyWith(),
                  ),
                ],
              );
            },
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
