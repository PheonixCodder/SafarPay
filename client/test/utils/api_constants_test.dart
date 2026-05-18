import 'package:client/utils/constants/api_constants.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('resolves service base URLs', () {
    expect(
      SApiConstants.baseUrlFor(SApiService.auth),
      SApiConstants.authBaseUrl,
    );
    expect(
      SApiConstants.baseUrlFor(SApiService.location),
      SApiConstants.locationBaseUrl,
    );
    expect(
      SApiConstants.baseUrlFor(SApiService.geospatial),
      SApiConstants.geospatialBaseUrl,
    );
  });

  test('builds websocket URLs with existing query parameters preserved', () {
    final uri = SApiConstants.websocketUri(
      SApiService.location,
      '/ws/rides/ride-1/track',
      queryParameters: {'token': 'jwt-token'},
    );

    expect(uri.scheme, anyOf('ws', 'wss'));
    expect(uri.path, endsWith('/ws/rides/ride-1/track'));
    expect(uri.queryParameters['token'], 'jwt-token');
  });
}
