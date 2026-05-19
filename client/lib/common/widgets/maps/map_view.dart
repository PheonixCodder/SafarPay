import 'package:flutter/material.dart';
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart';

import '../../../features/location/data/mapbox_config.dart';
import '../../../features/location/domain/location_models.dart';
import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/helpers/helpers.dart';
import 'map_models.dart';

class SMapView extends StatefulWidget {
  const SMapView({
    super.key,
    required this.initialCenter,
    this.controller,
    this.markers = const [],
    this.route,
    this.zoom = 13,
    this.isLoading = false,
    this.errorMessage,
    this.fullBleed = false,
    this.showStatusPill = true,
    this.showRecenterButton = true,
    this.showCenterPin = false,
    this.borderRadius,
    this.onRecenter,
    this.onMapCreated,
  });

  final SCoordinate initialCenter;
  final SMapController? controller;
  final List<SMapMarker> markers;
  final SRoutePreview? route;
  final double zoom;
  final bool isLoading;
  final String? errorMessage;
  final bool fullBleed;
  final bool showStatusPill;
  final bool showRecenterButton;
  final bool showCenterPin;
  final double? borderRadius;
  final VoidCallback? onRecenter;
  final ValueChanged<MapboxMap>? onMapCreated;

  @override
  State<SMapView> createState() => _SMapViewState();
}

class _SMapViewState extends State<SMapView> {
  MapboxMap? _mapboxMap;

  @override
  Widget build(BuildContext context) {
    if (SMapboxConfig.shouldBlockMapRendering) {
      return const _MapUnavailable(
        message: 'Map configuration is unavailable.',
      );
    }

    return Stack(
      children: [
        ClipRRect(
          borderRadius: BorderRadius.circular(
            widget.borderRadius ?? (widget.fullBleed ? 0 : SSizes.cardRadiusLg),
          ),
          child: MapWidget(
            key: const ValueKey('safarpay-map'),
            styleUri: MapboxStyles.MAPBOX_STREETS,
            // The SDK still accepts cameraOptions and the newer viewport API
            // requires a broader camera-state model than this wrapper owns.
            // ignore: deprecated_member_use
            cameraOptions: CameraOptions(
              center: Point(
                coordinates: Position(
                  widget.initialCenter.longitude,
                  widget.initialCenter.latitude,
                ),
              ),
              zoom: widget.zoom,
            ),
            onMapCreated: _handleMapCreated,
          ),
        ),
        if (widget.showStatusPill)
          Positioned(
            left: SSizes.md,
            top: SSizes.md,
            right: SSizes.md,
            child: _MapStatusPill(
              markers: widget.markers,
              route: widget.route,
              errorMessage: widget.errorMessage,
            ),
          ),
        if (widget.showCenterPin)
          const Center(
            child: _MapCenterPin(),
          ),
        if (widget.showCenterPin)
          const Center(
            child: Padding(
              padding: EdgeInsets.only(top: 44),
              child: _MapPinShadow(),
            ),
          ),
        if (widget.isLoading)
          Positioned.fill(
            child: ColoredBox(
              color: SHelperFunctions.withOpacity(
                SColors.white,
                SOpacities.strong,
              ),
              child: Center(child: CircularProgressIndicator()),
            ),
          ),
        if (widget.showRecenterButton)
          Positioned(
            right: SSizes.md,
            bottom: SSizes.md,
            child: FloatingActionButton.small(
              heroTag: 's-map-recenter',
              backgroundColor: SColors.white,
              foregroundColor: SColors.primary,
              onPressed: widget.onRecenter ?? _recenter,
              child: const Icon(Icons.my_location),
            ),
          ),
      ],
    );
  }

  Future<void> _handleMapCreated(MapboxMap mapboxMap) async {
    _mapboxMap = mapboxMap;
    await mapboxMap.location.updateSettings(
      LocationComponentSettings(
        enabled: true,
        pulsingEnabled: true,
      ),
    );
    widget.controller?.attachCameraReader(_centerCoordinate);
    widget.onMapCreated?.call(mapboxMap);
  }

  Future<SCoordinate?> _centerCoordinate() async {
    final camera = await _mapboxMap?.getCameraState();
    final center = camera?.center.coordinates;
    final latitude = center?.lat.toDouble();
    final longitude = center?.lng.toDouble();
    if (latitude == null || longitude == null) return null;

    return SCoordinate(latitude: latitude, longitude: longitude);
  }

  Future<void> _recenter() async {
    await _mapboxMap?.flyTo(
      CameraOptions(
        center: Point(
          coordinates: Position(
            widget.initialCenter.longitude,
            widget.initialCenter.latitude,
          ),
        ),
        zoom: widget.zoom,
      ),
      MapAnimationOptions(duration: 500),
    );
  }
}

class _MapCenterPin extends StatelessWidget {
  const _MapCenterPin();

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.radiusFull),
        boxShadow: [
          BoxShadow(
            color: SHelperFunctions.withOpacity(
              SColors.pureBlack,
              SOpacities.shadow,
            ),
            blurRadius: SSizes.shadowBlurLg,
            offset: const Offset(0, SSizes.sm),
          ),
        ],
      ),
      child: const Padding(
        padding: EdgeInsets.all(SSizes.sm),
        child: Icon(
          Icons.location_pin,
          color: SColors.primary,
          size: SSizes.iconLg,
        ),
      ),
    );
  }
}

class _MapPinShadow extends StatelessWidget {
  const _MapPinShadow();

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: SHelperFunctions.withOpacity(
          SColors.pureBlack,
          SOpacities.placeholder,
        ),
        borderRadius: BorderRadius.circular(SSizes.radiusFull),
      ),
      child: const SizedBox(width: 22, height: 6),
    );
  }
}

class _MapStatusPill extends StatelessWidget {
  const _MapStatusPill({
    required this.markers,
    required this.route,
    required this.errorMessage,
  });

  final List<SMapMarker> markers;
  final SRoutePreview? route;
  final String? errorMessage;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final message = errorMessage ??
        (route == null
            ? '${markers.length} map point${markers.length == 1 ? '' : 's'}'
            : '${route!.distanceKm.toStringAsFixed(1)} km - ${route!.durationMinutes.round()} min');

    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.radiusFull),
        boxShadow: [
          BoxShadow(
            color: SHelperFunctions.withOpacity(
              SColors.pureBlack,
              SOpacities.light,
            ),
            blurRadius: SSizes.shadowBlurLg,
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: SSizes.md,
          vertical: SSizes.sm,
        ),
        child: Text(
          message,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: textTheme.labelLarge?.copyWith(
            color: errorMessage == null ? SColors.textPrimary : SColors.error,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}

class _MapUnavailable extends StatelessWidget {
  const _MapUnavailable({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: SColors.lightContainer,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(SSizes.lg),
          child: Text(
            message,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: SColors.textSecondary,
                ),
          ),
        ),
      ),
    );
  }
}

