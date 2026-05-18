import 'package:flutter/foundation.dart';
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart';

import '../../../utils/constants/api_constants.dart';
import '../../../utils/logging/logger.dart';

class SMapboxConfig {
  SMapboxConfig._();

  static bool get hasToken => SApiConstants.mapboxAccessToken.isNotEmpty;

  static void initialize() {
    if (!hasToken) {
      SLoggerHelper.warning('MAPBOX_ACCESS_TOKEN is not configured.');
      return;
    }

    MapboxOptions.setAccessToken(SApiConstants.mapboxAccessToken);
  }

  static bool get shouldBlockMapRendering {
    return !hasToken && kReleaseMode;
  }
}
