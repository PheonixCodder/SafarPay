import 'demo/location_demo_data.dart';
import '../domain/location_models.dart';

class SLocationRepository {
  const SLocationRepository();

  Future<SAddressResult> geocode(String address) async {
    return SLocationDemoData.geocode(address);
    // final data = await SHttpClient.post(
    //   '/geocode',
    //   service: SApiService.location,
    //   requiresAuth: true,
    //   body: {'address': address},
    // );
    // return SAddressResult.fromJson(data);
  }

  Future<SAddressResult> reverseGeocode(SCoordinate coordinate) async {
    return SLocationDemoData.reverseGeocode(coordinate);
    // final data = await SHttpClient.post(
    //   '/reverse',
    //   service: SApiService.location,
    //   requiresAuth: true,
    //   body: {
    //     'latitude': coordinate.latitude,
    //     'longitude': coordinate.longitude,
    //   },
    // );
    // return SAddressResult.fromJson(data);
  }

  Future<SLiveRideLocations> getRideLocations(String rideId) async {
    return SLocationDemoData.liveRideLocations(rideId);
    // final data = await SHttpClient.get(
    //   '/rides/$rideId/locations',
    //   service: SApiService.location,
    //   requiresAuth: true,
    // );
    // return SLiveRideLocations.fromJson(data);
  }
}
