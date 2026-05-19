import 'package:client/common/widgets/ride/search_result.dart';
import 'package:client/features/location/domain/location_models.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

class SBookingSearchResults extends StatelessWidget {
  const SBookingSearchResults({
    super.key,
    required this.isLoading,
    required this.errorMessage,
    required this.results,
    required this.onSelected,
  });

  final bool isLoading;
  final String errorMessage;
  final List<SAddressResult> results;
  final ValueChanged<SAddressResult> onSelected;

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Padding(
        padding: EdgeInsets.all(SSizes.lg),
        child: Center(child: CircularProgressIndicator()),
      );
    }

    if (results.isEmpty) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: SSizes.lg),
        child: Text(
          errorMessage.isEmpty
              ? 'Search for a pickup or destination.'
              : errorMessage,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: SColors.textSecondary,
              ),
        ),
      );
    }

    return Column(
      children: [
        for (final result in results)
          SSearchResult(
            icon: Iconsax.location,
            title: result.formatted,
            address: [
              if (result.city != null) result.city,
              if (result.country != null) result.country,
            ].whereType<String>().join(', '),
            duration: 'Select',
            onTap: () => onSelected(result),
            showDivider: result != results.last,
          ),
      ],
    );
  }
}
