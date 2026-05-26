import 'dart:async';

import 'package:flutter/material.dart';
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart';

import '../../../features/location/data/mapbox_config.dart';
import '../../../features/location/domain/location_models.dart';
import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/helpers/helpers.dart';
import 'map_camera_targets.dart';
import 'map_models.dart';
import 'map_route_geometry.dart';

class SMapView extends StatefulWidget {
  const SMapView({
    super.key,
    required this.initialCenter,
    this.controller,
    this.markers = const [],
    this.route,
    this.zoom = 13,
    this.maxFitZoom = 16,
    this.cameraMode = SMapCameraMode.manual,
    this.fitPadding = const EdgeInsets.all(56),
    this.isLoading = false,
    this.errorMessage,
    this.fullBleed = false,
    this.showStatusPill = true,
    this.showRecenterButton = true,
    this.showCenterPin = false,
    this.showUserLocation = false,
    this.borderRadius,
    this.onRecenter,
    this.onMapCreated,
  });

  final SCoordinate initialCenter;
  final SMapController? controller;
  final List<SMapMarker> markers;
  final SRoutePreview? route;
  final double zoom;
  final double maxFitZoom;
  final SMapCameraMode cameraMode;
  final EdgeInsets fitPadding;
  final bool isLoading;
  final String? errorMessage;
  final bool fullBleed;
  final bool showStatusPill;
  final bool showRecenterButton;
  final bool showCenterPin;
  final bool showUserLocation;
  final double? borderRadius;
  final VoidCallback? onRecenter;
  final ValueChanged<MapboxMap>? onMapCreated;

  @override
  State<SMapView> createState() => _SMapViewState();
}

class _SMapViewState extends State<SMapView> {
  MapboxMap? _mapboxMap;
  CircleAnnotationManager? _markerManager;
  PointAnnotationManager? _labelManager;
  PolylineAnnotationManager? _routeManager;

  @override
  void didUpdateWidget(covariant SMapView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.markers != widget.markers ||
        oldWidget.route != widget.route) {
      unawaited(_syncMapAnnotations());
    }
    if (oldWidget.markers != widget.markers ||
        oldWidget.route != widget.route ||
        oldWidget.cameraMode != widget.cameraMode ||
        oldWidget.initialCenter != widget.initialCenter) {
      unawaited(_syncCamera(animated: true));
    }
  }

  @override
  void dispose() {
    final markerManager = _markerManager;
    final labelManager = _labelManager;
    final routeManager = _routeManager;
    if (markerManager != null) unawaited(markerManager.deleteAll());
    if (labelManager != null) unawaited(labelManager.deleteAll());
    if (routeManager != null) unawaited(routeManager.deleteAll());
    super.dispose();
  }

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
              heroTag: null,
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
    _routeManager =
        await mapboxMap.annotations.createPolylineAnnotationManager();
    _markerManager =
        await mapboxMap.annotations.createCircleAnnotationManager();
    _labelManager = await mapboxMap.annotations.createPointAnnotationManager();
    await mapboxMap.location.updateSettings(
      LocationComponentSettings(
        enabled: widget.showUserLocation,
        pulsingEnabled: widget.showUserLocation,
      ),
    );
    widget.controller?.attachCameraReader(_centerCoordinate);
    await _syncMapAnnotations();
    await _syncCamera(animated: false);
    widget.onMapCreated?.call(mapboxMap);
  }

  Future<void> _syncMapAnnotations() async {
    await _syncRouteAnnotation();
    await _syncMarkerAnnotations();
  }

  Future<void> _syncRouteAnnotation() async {
    final routeManager = _routeManager;
    if (routeManager == null) return;

    await routeManager.deleteAll();

    final coordinates = SMapRouteGeometry.coordinatesForRoute(
      route: widget.route,
      markers: widget.markers
          .map(
            (marker) => SMapRoutePoint(
              id: marker.id,
              coordinate: marker.coordinate,
              isPickup: marker.type == SMapMarkerType.pickup,
            ),
          )
          .toList(),
    );
    if (coordinates.length < 2) return;

    await routeManager.create(
      PolylineAnnotationOptions(
        geometry: LineString(
          coordinates: coordinates
              .map(
                (coordinate) => Position(
                  coordinate.longitude,
                  coordinate.latitude,
                ),
              )
              .toList(),
        ),
        lineColor: SColors.primary.toARGB32(),
        lineWidth: 5,
      ),
    );
  }

  Future<void> _syncMarkerAnnotations() async {
    final markerManager = _markerManager;
    final labelManager = _labelManager;
    if (markerManager == null) return;

    await markerManager.deleteAll();
    await labelManager?.deleteAll();
    if (widget.markers.isEmpty) return;

    await markerManager.createMulti(
      widget.markers
          .map(
            (marker) => CircleAnnotationOptions(
              geometry: Point(
                coordinates: Position(
                  marker.coordinate.longitude,
                  marker.coordinate.latitude,
                ),
              ),
              circleColor: _markerColor(marker.type).toARGB32(),
              circleRadius: _markerRadius(marker.type),
              circleStrokeColor: SColors.white.toARGB32(),
              circleStrokeWidth: _markerStrokeWidth(marker.type),
              circleOpacity: marker.isStale ? 0.55 : 1,
            ),
          )
          .toList(),
    );
    await labelManager?.createMulti(
      widget.markers
          .map(
            (marker) => PointAnnotationOptions(
              geometry: Point(
                coordinates: Position(
                  marker.coordinate.longitude,
                  marker.coordinate.latitude,
                ),
              ),
              textField: _markerText(marker.type),
              textSize: _markerTextSize(marker.type),
              textColor: SColors.white.toARGB32(),
              textHaloColor: _markerColor(marker.type).toARGB32(),
              textHaloWidth: 1,
              textOpacity: marker.isStale ? 0.65 : 1,
            ),
          )
          .toList(),
    );
  }

  Color _markerColor(SMapMarkerType type) {
    return switch (type) {
      SMapMarkerType.pickup => SColors.success,
      SMapMarkerType.dropoff => SColors.error,
      SMapMarkerType.driver => SColors.black,
      SMapMarkerType.passenger => SColors.primary,
    };
  }

  double _markerRadius(SMapMarkerType type) {
    return switch (type) {
      SMapMarkerType.driver => 12,
      SMapMarkerType.passenger => 11,
      SMapMarkerType.pickup || SMapMarkerType.dropoff => 12,
    };
  }

  double _markerStrokeWidth(SMapMarkerType type) {
    return switch (type) {
      SMapMarkerType.driver => 4,
      SMapMarkerType.passenger => 4,
      SMapMarkerType.pickup || SMapMarkerType.dropoff => 3.5,
    };
  }

  String _markerText(SMapMarkerType type) {
    return switch (type) {
      SMapMarkerType.pickup => 'P',
      SMapMarkerType.dropoff => 'D',
      SMapMarkerType.driver => 'DR',
      SMapMarkerType.passenger => 'YOU',
    };
  }

  double _markerTextSize(SMapMarkerType type) {
    return switch (type) {
      SMapMarkerType.driver => 9,
      SMapMarkerType.passenger => 8,
      SMapMarkerType.pickup || SMapMarkerType.dropoff => 11,
    };
  }

  Future<void> _syncCamera({required bool animated}) async {
    if (widget.cameraMode == SMapCameraMode.manual) return;
    final mapboxMap = _mapboxMap;
    if (mapboxMap == null) return;

    final coordinates = _cameraCoordinates();
    if (coordinates.isEmpty) return;

    if (coordinates.length == 1) {
      await _moveCamera(
        CameraOptions(
          center: _pointFor(coordinates.first),
          zoom: _targetZoom(),
          pitch: _targetPitch(),
        ),
        animated: animated,
      );
      return;
    }

    final camera = await mapboxMap.cameraForCoordinatesPadding(
      coordinates.map(_pointFor).toList(),
      CameraOptions(),
      MbxEdgeInsets(
        top: widget.fitPadding.top,
        left: widget.fitPadding.left,
        bottom: widget.fitPadding.bottom,
        right: widget.fitPadding.right,
      ),
      widget.maxFitZoom,
      null,
    );
    await _moveCamera(camera, animated: animated);
  }

  List<SCoordinate> _cameraCoordinates() {
    return SMapCameraTargets.coordinates(
      mode: widget.cameraMode,
      route: widget.route,
      markers: widget.markers,
    );
  }

  double _targetZoom() {
    if (widget.cameraMode == SMapCameraMode.navigationFollow) return 17.35;
    return widget.zoom;
  }

  double? _targetPitch() {
    if (widget.cameraMode == SMapCameraMode.navigationFollow) return 45;
    return null;
  }

  Future<void> _moveCamera(
    CameraOptions cameraOptions, {
    required bool animated,
  }) async {
    if (animated) {
      await _mapboxMap?.flyTo(
        cameraOptions,
        MapAnimationOptions(duration: 500),
      );
      return;
    }
    await _mapboxMap?.setCamera(cameraOptions);
  }

  Point _pointFor(SCoordinate coordinate) {
    return Point(
      coordinates: Position(
        coordinate.longitude,
        coordinate.latitude,
      ),
    );
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
    if (widget.cameraMode != SMapCameraMode.manual) {
      await _syncCamera(animated: true);
      return;
    }
    await _moveCamera(
      CameraOptions(
        center: _pointFor(widget.initialCenter),
        zoom: widget.zoom,
      ),
      animated: true,
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
