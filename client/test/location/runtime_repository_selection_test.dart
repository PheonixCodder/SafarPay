import 'package:client/common/runtime/runtime_mode.dart';
import 'package:client/features/location/data/bidding_repository.dart';
import 'package:client/features/location/data/bidding_socket_repository.dart';
import 'package:client/features/location/data/geospatial_repository.dart';
import 'package:client/features/location/data/live_ride_socket_repository.dart';
import 'package:client/features/location/data/location_repository.dart';
import 'package:client/features/location/data/ride_repository.dart';
import 'package:client/features/location/data/ride_socket_repository.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('runtime repository selection', () {
    test('location repository exposes selected runtime data source', () {
      expect(
        const SLocationRepository(useDemoData: true).runtimeDataSource,
        SRuntimeDataSource.demo,
      );
      expect(
        const SLocationRepository(useDemoData: false).runtimeDataSource,
        SRuntimeDataSource.real,
      );
    });

    test('geospatial repository exposes selected runtime data source', () {
      expect(
        const SGeospatialRepository(useDemoData: true).runtimeDataSource,
        SRuntimeDataSource.demo,
      );
      expect(
        const SGeospatialRepository(useDemoData: false).runtimeDataSource,
        SRuntimeDataSource.real,
      );
    });

    test('bidding repository exposes selected runtime data source', () {
      expect(
        const SBiddingRepository(useDemoData: true).runtimeDataSource,
        SRuntimeDataSource.demo,
      );
      expect(
        const SBiddingRepository(useDemoData: false).runtimeDataSource,
        SRuntimeDataSource.real,
      );
    });

    test('ride repository exposes selected runtime data source', () {
      expect(
        const SRideRepository(useDemoData: true).runtimeDataSource,
        SRuntimeDataSource.demo,
      );
      expect(
        const SRideRepository(useDemoData: false).runtimeDataSource,
        SRuntimeDataSource.real,
      );
    });

    test('socket repositories expose selected runtime data source', () {
      expect(
        SBiddingSocketRepository(useDemoData: true).runtimeDataSource,
        SRuntimeDataSource.demo,
      );
      expect(
        SRideSocketRepository(useDemoData: false).runtimeDataSource,
        SRuntimeDataSource.real,
      );
      expect(
        SLiveRideSocketRepository(useDemoData: true).runtimeDataSource,
        SRuntimeDataSource.demo,
      );
    });
  });
}
