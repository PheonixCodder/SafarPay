import 'package:flutter/material.dart';
import 'package:get/get.dart';

import '../../../../../../../common/navigation/right_slide_page_route.dart';
import '../../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../../navigation_menu.dart';
import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../models/support_ticket_models.dart';
import '../widgets/support_success_illustration.dart';
import '../widgets/support_ticket_summary_card.dart';
import 'my_tickets_screen.dart';

class TicketCreatedScreen extends StatelessWidget {
  const TicketCreatedScreen({
    super.key,
    required this.response,
  });

  final SSupportTicketCreateResponse response;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(showBackArrow: true),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: SSizes.md),
                  const SSupportSuccessIllustration(),
                  const SizedBox(height: SSizes.lg),
                  Text(
                    'Ticket Created Successfully!',
                    textAlign: TextAlign.center,
                    style: textTheme.headlineSmall?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w900,
                      height: 1.1,
                    ),
                  ),
                  const SizedBox(height: SSizes.sm),
                  Text(
                    response.message,
                    textAlign: TextAlign.center,
                    style: textTheme.bodyMedium?.copyWith(
                      color: SColors.textSecondary,
                      height: 1.35,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  const SizedBox(height: SSizes.xl),
                  SSupportTicketSummaryCard(response: response),
                  const SizedBox(height: SSizes.lg),
                  ElevatedButton(
                    onPressed: () => Navigator.of(context).push(
                      SRightSlidePageRoute(
                        page: MyTicketsScreen(ticket: response),
                      ),
                    ),
                    child: const Text('Go to My Tickets'),
                  ),
                  const SizedBox(height: SSizes.md),
                  TextButton(
                    onPressed: () => Get.offAll(() => const NavigationMenu()),
                    child: const Text('Back to Home'),
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
