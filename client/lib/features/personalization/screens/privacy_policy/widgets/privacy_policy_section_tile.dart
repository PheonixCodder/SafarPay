import 'package:flutter/material.dart';

import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/helpers/helpers.dart';
import '../models/privacy_policy_section.dart';

class SPrivacyPolicySectionTile extends StatelessWidget {
  const SPrivacyPolicySectionTile({
    super.key,
    required this.section,
  });

  final SPrivacyPolicySection section;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(SSizes.privacyPolicyTileRadius),
      child: Material(
        color: SColors.white,
        child: ExpansionTile(
          tilePadding: const EdgeInsets.symmetric(
            horizontal: SSizes.md,
            vertical: SSizes.sm,
          ),
          childrenPadding: const EdgeInsets.fromLTRB(
            SSizes.md,
            0,
            SSizes.md,
            SSizes.md,
          ),
          iconColor: SColors.primary,
          collapsedIconColor: SColors.textSecondary,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(SSizes.privacyPolicyTileRadius),
            side: const BorderSide(color: SColors.borderSecondary),
          ),
          collapsedShape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(SSizes.privacyPolicyTileRadius),
            side: const BorderSide(color: SColors.borderSecondary),
          ),
          leading: Container(
            width: SSizes.profileEditIconBoxSize,
            height: SSizes.profileEditIconBoxSize,
            decoration: BoxDecoration(
              color: SHelperFunctions.withOpacity(
                SColors.primary,
                SOpacities.placeholder,
              ),
              borderRadius: BorderRadius.circular(SSizes.profileEditIconRadius),
            ),
            child: Icon(
              section.icon,
              color: SColors.primary,
              size: SSizes.profileEditIconSize,
            ),
          ),
          title: Text(
            section.title,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          subtitle: Text(
            section.summary,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: SColors.textSecondary,
                ),
          ),
          children: [
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                section.body,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: SColors.textSecondary,
                      height: 1.55,
                    ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
