import 'package:flutter/material.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';
import '../models/support_ticket_models.dart';

class SSupportTicketSummaryCard extends StatelessWidget {
  const SSupportTicketSummaryCard({
    super.key,
    required this.response,
  });

  final SSupportTicketCreateResponse response;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Column(
        children: [
          _SummaryRow(
            label: 'Ticket ID',
            value: response.ticketId,
          ),
          const Divider(height: SSizes.dividerHeight),
          _SummaryRow(
            label: 'Expected response',
            value: 'Within ${response.expectedResponseMinutes} minutes',
          ),
        ],
      ),
    );
  }
}

class _SummaryRow extends StatelessWidget {
  const _SummaryRow({
    required this.label,
    required this.value,
  });

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Padding(
      padding: const EdgeInsets.all(SSizes.md),
      child: Align(
        alignment: Alignment.centerLeft,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: textTheme.labelMedium?.copyWith(
                color: SColors.textSecondary,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: SSizes.xs),
            Text(
              value,
              style: textTheme.titleSmall?.copyWith(
                color: SColors.textPrimary,
                fontWeight: FontWeight.w900,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
