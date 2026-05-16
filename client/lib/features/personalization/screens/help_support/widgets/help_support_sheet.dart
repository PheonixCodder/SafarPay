import 'package:flutter/material.dart';

import '../../../../../common/navigation/right_slide_page_route.dart';
import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';
import '../help_support_content.dart';
import 'help_support_option_tile.dart';

class SHelpSupportSheet extends StatelessWidget {
  const SHelpSupportSheet({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(
        SSizes.defaultSpace,
        SSizes.lg,
        SSizes.defaultSpace,
        SSizes.defaultSpace,
      ),
      decoration: const BoxDecoration(
        color: SColors.primaryBackground,
        borderRadius: BorderRadius.vertical(
          top: Radius.circular(SSizes.helpSupportSheetRadius),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            STexts.helpSupportQuestion,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: SColors.pureBlack,
                  fontWeight: FontWeight.w700,
                ),
          ),
          const SizedBox(height: SSizes.lg),
          for (final option in SHelpSupportContent.options)
            SHelpSupportOptionTile(
              option: option,
              onTap: () => Navigator.of(context).push(
                SRightSlidePageRoute(page: option.destination),
              ),
            ),
        ],
      ),
    );
  }
}
