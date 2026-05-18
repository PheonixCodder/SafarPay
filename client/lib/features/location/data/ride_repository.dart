import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import '../domain/location_models.dart';

class SRideRepository {
  const SRideRepository();

  static Map<String, dynamic> buildCityRideRequest({
    required SAddressResult pickup,
    required SAddressResult dropoff,
  }) {
    return {
      'service_type': 'CITY_RIDE',
      'category': 'MINI',
      'pricing_mode': 'FIXED',
      'stops': [
        _stopPayload(
          sequenceOrder: 1,
          stopType: 'PICKUP',
          address: pickup,
        ),
        _stopPayload(
          sequenceOrder: 2,
          stopType: 'DROPOFF',
          address: dropoff,
        ),
      ],
      'detail': {
        'service_type': 'CITY_RIDE',
        'passenger_count': 1,
        'is_ac': false,
        'is_shared_ride': false,
        'requires_otp_start': true,
        'requires_otp_end': true,
      },
      'auto_accept_driver': true,
      'passenger_payment_method': 'CASH',
    };
  }

  Future<Map<String, dynamic>> createRide(Map<String, dynamic> body) {
    return SHttpClient.post(
      '/rides',
      service: SApiService.ride,
      requiresAuth: true,
      body: body,
    );
  }

  Future<Map<String, dynamic>> fetchRide(String rideId) {
    return SHttpClient.get(
      '/rides/$rideId',
      service: SApiService.ride,
      requiresAuth: true,
    );
  }

  Future<Map<String, dynamic>> cancelRide({
    required String rideId,
    required String reason,
  }) {
    return SHttpClient.post(
      '/rides/$rideId/cancel',
      service: SApiService.ride,
      requiresAuth: true,
      body: {'reason': reason},
    );
  }
}

Map<String, dynamic> _stopPayload({
  required int sequenceOrder,
  required String stopType,
  required SAddressResult address,
}) {
  return {
    'sequence_order': sequenceOrder,
    'stop_type': stopType,
    'latitude': address.coordinate.latitude,
    'longitude': address.coordinate.longitude,
    'place_name': address.formatted,
    'address_line_1': address.formatted,
    'city': address.city,
    'country': address.country,
    'postal_code': address.postalCode,
  };
}
