import 'dart:io';

import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/constants/texts.dart';
import '../../../utils/helpers/helpers.dart';

class SImageUploadTile extends StatelessWidget {
  const SImageUploadTile({
    super.key,
    required this.title,
    required this.subtitle,
    required this.onTakePhoto,
    required this.onPickImage,
    this.imagePath,
    this.onRemove,
    this.isRequired = true,
  });

  final String title;
  final String subtitle;
  final String? imagePath;
  final VoidCallback onTakePhoto;
  final VoidCallback onPickImage;
  final VoidCallback? onRemove;
  final bool isRequired;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final hasImage = imagePath != null && imagePath!.isNotEmpty;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(SSizes.md),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: SHelperFunctions.withOpacity(
                    hasImage ? SColors.success : SColors.primary,
                    SOpacities.tinted,
                  ),
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
                ),
                child: Icon(
                  hasImage ? Iconsax.tick_circle : Iconsax.document_upload,
                  color: hasImage ? SColors.success : SColors.primary,
                  size: SSizes.iconMd,
                ),
              ),
              const SizedBox(width: SSizes.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isRequired ? '$title *' : title,
                      style: textTheme.titleSmall?.copyWith(
                        color: SColors.textPrimary,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    const SizedBox(height: SSizes.xs),
                    Text(
                      subtitle,
                      style: textTheme.bodySmall?.copyWith(
                        color: SColors.textSecondary,
                        height: 1.3,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (hasImage) ...[
            const SizedBox(height: SSizes.md),
            ClipRRect(
              borderRadius: BorderRadius.circular(SSizes.cardRadiusMd),
              child: AspectRatio(
                aspectRatio: 16 / 9,
                child: Image.file(
                  File(imagePath!),
                  fit: BoxFit.cover,
                ),
              ),
            ),
          ],
          const SizedBox(height: SSizes.md),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onTakePhoto,
                  icon: const Icon(Iconsax.camera, size: SSizes.iconSm),
                  label: const Text(STexts.driverRegistrationCamera),
                ),
              ),
              const SizedBox(width: SSizes.sm),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onPickImage,
                  icon: const Icon(Iconsax.gallery, size: SSizes.iconSm),
                  label: const Text(STexts.driverRegistrationGallery),
                ),
              ),
              if (hasImage && onRemove != null) ...[
                const SizedBox(width: SSizes.sm),
                IconButton(
                  onPressed: onRemove,
                  icon: const Icon(Iconsax.trash, color: SColors.error),
                  tooltip: STexts.driverRegistrationRemoveImage,
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}
