import 'package:flutter/material.dart';

import '../../../../../../../common/navigation/right_slide_page_route.dart';
import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../../../../../../../utils/helpers/helpers.dart';
import '../models/terms_policy.dart';
import '../screens/terms_policy_detail.dart';
import 'terms_policy_tile.dart';

class STermsPolicyListCard extends StatelessWidget {
  const STermsPolicyListCard({
    super.key,
    required this.policies,
  });

  final List<STermsPolicy> policies;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (final policy in policies)
          Padding(
            padding: const EdgeInsets.only(bottom: SSizes.md),
            child: Container(
              decoration: BoxDecoration(
                color: SColors.white,
                borderRadius: BorderRadius.circular(
                  SSizes.cardRadiusLg,
                ),
                border: Border.all(
                  color: SColors.borderSecondary,
                ),
                boxShadow: [
                  BoxShadow(
                    color: SHelperFunctions.withOpacity(
                      SColors.pureBlack,
                      0.04,
                    ),
                    blurRadius: 16,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: SSizes.sm,
                  vertical: SSizes.xs,
                ),
                child: STermsPolicyTile(
                  policy: policy,
                  onTap: () => Navigator.of(context).push(
                    SRightSlidePageRoute(
                      page: TermsPolicyDetailScreen(
                        policy: policy,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}