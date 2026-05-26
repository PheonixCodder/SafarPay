import 'package:client/data/rides/ride_models.dart';
import 'package:client/features/location/controllers/ride_search_controller.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SRidePricingOptions extends StatelessWidget {
  const SRidePricingOptions({super.key, required this.controller});

  final SRideSearchController controller;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Obx(
      () => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Price and payment',
            style: textTheme.titleMedium?.copyWith(
              color: SColors.textPrimary,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: SSizes.sm),
          SegmentedButton<PricingMode>(
            segments: const [
              ButtonSegment(value: PricingMode.fixed, label: Text('Fixed')),
              ButtonSegment(value: PricingMode.hybrid, label: Text('Hybrid')),
            ],
            selected: {controller.pricingMode.value},
            onSelectionChanged: (value) =>
                controller.pricingMode.value = value.first,
          ),
          const SizedBox(height: SSizes.sm),
          Wrap(
            spacing: SSizes.xs,
            runSpacing: SSizes.xs,
            children: [
              for (final method in PassengerPaymentMethod.values)
                ChoiceChip(
                  label: Text(_paymentLabel(method)),
                  selected: controller.paymentMethod.value == method,
                  onSelected: (_) => controller.paymentMethod.value = method,
                ),
            ],
          ),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Schedule for later'),
            subtitle: Text(
              controller.scheduledAt.value == null
                  ? 'Book as soon as possible'
                  : 'About 1 hour from now',
            ),
            value: controller.scheduledAt.value != null,
            onChanged: controller.scheduleOneHourFromNow,
          ),
        ],
      ),
    );
  }

  String _paymentLabel(PassengerPaymentMethod method) {
    return switch (method) {
      PassengerPaymentMethod.cash => 'Cash',
      PassengerPaymentMethod.card => 'Card',
      PassengerPaymentMethod.easypaisa => 'Easypaisa',
      PassengerPaymentMethod.jazzcash => 'JazzCash',
    };
  }
}
