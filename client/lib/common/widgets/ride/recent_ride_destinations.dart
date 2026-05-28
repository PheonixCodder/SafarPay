import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../data/rides/ride_models.dart';
import '../../../features/location/data/geospatial_repository.dart';
import '../../../features/location/data/ride_repository.dart';
import '../../../features/location/domain/location_models.dart';
import '../../../utils/constants/sizes.dart';
import 'search_result.dart';

class SRecentRideDestinations extends StatefulWidget {
  const SRecentRideDestinations({
    super.key,
    required this.onSelected,
    this.origin,
    this.originFuture,
    this.limit = 3,
    this.title = 'Recent destinations',
    this.rideRepository = const SRideRepository(),
    this.geospatialRepository = const SGeospatialRepository(),
  });

  final ValueChanged<SAddressResult> onSelected;
  final SCoordinate? origin;
  final Future<SCoordinate?>? originFuture;
  final int limit;
  final String title;
  final SRideRepository rideRepository;
  final SGeospatialRepository geospatialRepository;

  @override
  State<SRecentRideDestinations> createState() =>
      _SRecentRideDestinationsState();
}

class _SRecentRideDestinationsState extends State<SRecentRideDestinations> {
  late Future<List<_RecentDestinationViewData>> _future;

  @override
  void initState() {
    super.initState();
    _future = _loadDestinations();
  }

  @override
  void didUpdateWidget(covariant SRecentRideDestinations oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.origin != widget.origin ||
        oldWidget.originFuture != widget.originFuture ||
        oldWidget.limit != widget.limit) {
      _future = _loadDestinations();
    }
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return FutureBuilder<List<_RecentDestinationViewData>>(
      future: _future,
      builder: (context, snapshot) {
        final destinations = snapshot.data ?? const [];
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Padding(
            padding: EdgeInsets.symmetric(vertical: SSizes.sm),
            child: LinearProgressIndicator(minHeight: 2),
          );
        }
        if (destinations.isEmpty) return const SizedBox.shrink();

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.title,
              style: textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: SSizes.xs),
            ...destinations.indexed.map((entry) {
              final index = entry.$1;
              final destination = entry.$2;
              return SSearchResult(
                icon: Iconsax.clock,
                title: destination.title,
                address: destination.address,
                duration: destination.durationLabel,
                showDivider: index != destinations.length - 1,
                onTap: () => widget.onSelected(destination.addressResult),
              );
            }),
          ],
        );
      },
    );
  }

  Future<List<_RecentDestinationViewData>> _loadDestinations() async {
    try {
      final origin = await _resolveOrigin();
      final destinations = await widget.rideRepository.listRecentDestinations(
        limit: widget.limit,
      );
      final viewData = <_RecentDestinationViewData>[];
      for (final destination in destinations) {
        final addressResult = _addressFromStop(destination.dropoffStop);
        final durationLabel = await _durationLabel(origin, addressResult);
        viewData.add(
          _RecentDestinationViewData(
            addressResult: addressResult,
            title: destination.dropoffStop.placeName?.trim().isNotEmpty == true
                ? destination.dropoffStop.placeName!.trim()
                : 'Recent destination',
            address: _formatAddress(destination.dropoffStop),
            durationLabel: durationLabel,
          ),
        );
      }
      return viewData;
    } catch (_) {
      return const [];
    }
  }

  Future<SCoordinate?> _resolveOrigin() {
    final origin = widget.origin;
    if (origin != null) return Future.value(origin);
    return widget.originFuture ?? Future<SCoordinate?>.value();
  }

  Future<String> _durationLabel(
    SCoordinate? origin,
    SAddressResult destination,
  ) async {
    if (origin == null) return 'Set pickup';
    try {
      final route = await widget.geospatialRepository.calculateRoute(
        origin: origin,
        destination: destination.coordinate,
      );
      final minutes = route.durationMinutes.round().clamp(1, 999);
      return '$minutes min';
    } catch (_) {
      return 'ETA off';
    }
  }
}

class _RecentDestinationViewData {
  const _RecentDestinationViewData({
    required this.addressResult,
    required this.title,
    required this.address,
    required this.durationLabel,
  });

  final SAddressResult addressResult;
  final String title;
  final String address;
  final String durationLabel;
}

SAddressResult _addressFromStop(StopResponse stop) {
  return SAddressResult(
    formatted: stop.placeName?.trim().isNotEmpty == true
        ? stop.placeName!.trim()
        : _formatAddress(stop),
    coordinate: SCoordinate(
      latitude: stop.latitude,
      longitude: stop.longitude,
    ),
    street: stop.addressLine1,
    city: stop.city,
    country: stop.country,
    postalCode: stop.postalCode,
  );
}

String _formatAddress(StopResponse stop) {
  final parts = <String>[
    if (stop.addressLine1 != null && stop.addressLine1!.trim().isNotEmpty)
      stop.addressLine1!.trim(),
    if (stop.addressLine2 != null && stop.addressLine2!.trim().isNotEmpty)
      stop.addressLine2!.trim(),
    if (stop.city != null && stop.city!.trim().isNotEmpty) stop.city!.trim(),
    if (stop.state != null && stop.state!.trim().isNotEmpty)
      stop.state!.trim(),
  ];
  return parts.isEmpty ? 'Address unavailable' : parts.join(', ');
}
