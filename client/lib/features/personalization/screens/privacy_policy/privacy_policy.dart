import 'package:flutter/material.dart';

import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import 'privacy_policy_content.dart';
import 'widgets/privacy_policy_footer.dart';
import 'widgets/privacy_policy_header.dart';
import 'widgets/privacy_policy_section_tile.dart';

class PrivacyPolicyScreen extends StatelessWidget {
  const PrivacyPolicyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text(STexts.privacyPolicyTitle),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          child: Column(
            children: [
              const SPrivacyPolicyHeader(),
              const SizedBox(height: SSizes.spaceBtnItems),
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: SPrivacyPolicyContent.sections.length,
                separatorBuilder: (context, index) =>
                    const SizedBox(height: SSizes.sm),
                itemBuilder: (context, index) => SPrivacyPolicySectionTile(
                  section: SPrivacyPolicyContent.sections[index],
                ),
              ),
              const SizedBox(height: SSizes.spaceBtnItems),
              const SPrivacyPolicyFooter(),
              const SizedBox(height: SSizes.spaceBtwSections),
            ],
          ),
        ),
      ),
    );
  }
}
