import 'package:flutter/material.dart';

import '../../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../models/support_ticket_models.dart';
import '../widgets/support_ticket_summary_card.dart';

class MyTicketsScreen extends StatelessWidget {
  const MyTicketsScreen({
    super.key,
    required this.ticket,
  });

  final SSupportTicketCreateResponse ticket;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text('My Tickets'),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Latest support ticket',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w900,
                    ),
              ),
              const SizedBox(height: SSizes.md),
              SSupportTicketSummaryCard(response: ticket),
            ],
          ),
        ),
      ),
    );
  }
}
