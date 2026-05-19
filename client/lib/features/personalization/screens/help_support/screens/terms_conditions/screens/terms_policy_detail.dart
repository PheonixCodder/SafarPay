import 'package:flutter/material.dart';

import '../../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../models/terms_policy.dart';
import '../widgets/terms_detail_section_tile.dart';
import '../widgets/terms_last_updated_label.dart';

class TermsPolicyDetailScreen extends StatelessWidget {
  const TermsPolicyDetailScreen({
    super.key,
    required this.policy,
  });

  final STermsPolicy policy;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: SAppBar(
        showBackArrow: true,
        title: Text(policy.title),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(
            SSizes.defaultSpace,
            SSizes.sm,
            SSizes.defaultSpace,
            SSizes.defaultSpace,
          ),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  STermsLastUpdatedLabel(lastUpdated: policy.lastUpdated),
                  const SizedBox(height: SSizes.lg),
                  DecoratedBox(
                    decoration: BoxDecoration(
                      color: SColors.white,
                      borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                      border: Border.all(color: SColors.borderSecondary),
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                      child: Column(
                        children: [
                          for (var index = 0;
                              index < policy.sections.length;
                              index++)
                            STermsDetailSectionTile(
                              index: index + 1,
                              title: policy.sections[index].title,
                              body: policy.sections[index].body,
                              initiallyExpanded: index == 0,
                            ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
