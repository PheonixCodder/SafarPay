import 'package:flutter/material.dart';

import '../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../common/widgets/containers/primary_header_container.dart';
import '../../../../../utils/constants/colors.dart';
import '../../../../../utils/constants/images.dart';
import '../../../../../utils/constants/sizes.dart';
import '../../../../../utils/constants/texts.dart';

class SHelpSupportHeader extends StatelessWidget {
  const SHelpSupportHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: SSizes.helpSupportHeaderHeight,
      child: ClipRect(
        child: OverflowBox(
          alignment: Alignment.topCenter,
          maxHeight: SSizes.primaryHeaderHeight,
          child: SPrimaryHeaderContainer(
            child: Column(
              children: [
                IconTheme(
                  data: const IconThemeData(color: SColors.white),
                  child: SAppBar(
                    showBackArrow: true,
                    title: Text(
                      STexts.helpSupportTitle,
                      style:
                          Theme.of(context).textTheme.headlineSmall?.copyWith(
                                color: SColors.white,
                                fontWeight: FontWeight.w700,
                              ),
                    ),
                  ),
                ),
                const SizedBox(height: SSizes.helpSupportImageTopSpacing),
                Image.asset(
                  SImages.supportScooter,
                  height: SSizes.helpSupportImageHeight,
                  fit: BoxFit.contain,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
