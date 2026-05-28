import '../../utils/constants/api_constants.dart';

enum SRuntimeDataSource { real, demo }

class SRuntimeModeConfig {
  const SRuntimeModeConfig({
    bool useLocationDemoData = SRuntimeModeConfig.useLocationDemoData,
  }) : _useLocationDemoData = useLocationDemoData;

  static const bool useLocationDemoData = SApiConstants.useLocationDemoData;
  static const SRuntimeModeConfig current = SRuntimeModeConfig();

  final bool _useLocationDemoData;

  SRuntimeDataSource get locationDataSource {
    return _useLocationDemoData
        ? SRuntimeDataSource.demo
        : SRuntimeDataSource.real;
  }

  bool get isUsingLocationDemoData {
    return locationDataSource == SRuntimeDataSource.demo;
  }
}
