import 'package:client/common/runtime/runtime_mode.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('SRuntimeModeConfig', () {
    test('selects demo location data source when demo flag is enabled', () {
      const config = SRuntimeModeConfig(useLocationDemoData: true);

      expect(config.locationDataSource, SRuntimeDataSource.demo);
      expect(config.isUsingLocationDemoData, isTrue);
    });

    test('selects real location data source when demo flag is disabled', () {
      const config = SRuntimeModeConfig(useLocationDemoData: false);

      expect(config.locationDataSource, SRuntimeDataSource.real);
      expect(config.isUsingLocationDemoData, isFalse);
    });
  });
}
