import 'package:flutter/material.dart';

import '../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../utils/constants/colors.dart';
import '../../../../../../utils/constants/sizes.dart';
import 'data/terms_conditions_data.dart';
import 'widgets/terms_last_updated_label.dart';
import 'widgets/terms_policy_list_card.dart';

class TermsConditionsScreen extends StatelessWidget {
  const TermsConditionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text('Terms & Conditions'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(
            SSizes.defaultSpace,
            SSizes.lg,
            SSizes.defaultSpace,
            SSizes.xl,
          ),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: SSizes.sm),

                  const STermsPolicyListCard(
                    policies: STermsConditionsData.policies,
                  ),

                  const SizedBox(height: SSizes.xl),

                  STermsLastUpdatedLabel(
                    lastUpdated: STermsConditionsData.lastUpdated,
                  ),

                  const SizedBox(height: SSizes.lg),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}