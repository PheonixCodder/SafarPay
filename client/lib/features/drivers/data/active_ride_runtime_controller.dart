import '../../../utils/constants/api_constants.dart';
import '../../../utils/http/client.dart';
import '../../../utils/local_storage/token_storage.dart';
import '../../../common/runtime/runtime_diagnostics_controller.dart';
import '../../rides/domain/ride_lifecycle.dart';
import '../../rides/orchestration/ride_realtime_orchestrator.dart';
import '../domain/active_ride_runtime_models.dart';

class SActiveRideRuntimeController {
  SActiveRideRuntimeController({
    required SActiveRideRuntimeService service,
    Future<String?> Function()? accessTokenProvider,
    Future<String?> Function()? refreshTokenProvider,
    String locationBaseUrl = SApiConstants.locationBaseUrl,
    String authBaseUrl = SApiConstants.authBaseUrl,
    SRideRealtimeOrchestrator? realtimeOrchestrator,
    SRuntimeDiagnosticsController? diagnosticsController,
  })  : _service = service,
        _accessTokenProvider =
            accessTokenProvider ?? SHttpClient.accessTokenForSocket,
        _refreshTokenProvider =
            refreshTokenProvider ?? STokenStorage.refreshToken,
        _locationBaseUrl = locationBaseUrl,
        _authBaseUrl = authBaseUrl,
        _realtimeOrchestrator =
            realtimeOrchestrator ?? SRideRealtimeOrchestrator(),
        _diagnosticsController = diagnosticsController;

  final SActiveRideRuntimeService _service;
  final Future<String?> Function() _accessTokenProvider;
  final Future<String?> Function() _refreshTokenProvider;
  final String _locationBaseUrl;
  final String _authBaseUrl;
  final SRideRealtimeOrchestrator _realtimeOrchestrator;
  final SRuntimeDiagnosticsController? _diagnosticsController;
  String? _currentRideId;
  String? _currentStatus;

  String? get currentRideId => _currentRideId;

  Future<void> syncActiveRide({
    required String driverId,
    required String rideId,
    required String status,
  }) async {
    final snapshot = SRideLifecycleSnapshot.fromDriverState(
      rideId: rideId,
      pricingMode: 'FIXED',
      status: status,
      assignedDriverId: driverId,
    );
    if (!_realtimeOrchestrator.shouldRunDriverForegroundRuntime(snapshot) ||
        driverId.isEmpty ||
        rideId.isEmpty) {
      await stop();
      return;
    }

    if (_currentRideId == rideId && _currentStatus == status) return;
    if (_currentRideId != null) await _service.stop();

    final token = await _accessTokenProvider();
    if (token == null || token.isEmpty) {
      await stop();
      return;
    }
    final refreshToken = await _refreshTokenProvider();

    await _service.start(
      SActiveRideRuntimeConfig(
        driverId: driverId,
        rideId: rideId,
        locationBaseUrl: _locationBaseUrl,
        authBaseUrl: _authBaseUrl,
        accessToken: token,
        refreshToken: refreshToken,
        status: status,
      ),
    );
    _currentRideId = rideId;
    _currentStatus = status;
    _diagnosticsController?.updateForegroundRuntime(
      rideId: rideId,
      status: status,
      isRunning: true,
    );
  }

  Future<void> stop() async {
    _currentRideId = null;
    _currentStatus = null;
    _diagnosticsController?.updateForegroundRuntime(
      rideId: null,
      status: null,
      isRunning: false,
    );
    await _service.stop();
  }
}
