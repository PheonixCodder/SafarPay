import '../models/driver_registration_models.dart';
import '../../../../../utils/constants/api_constants.dart';
import '../../../../../utils/http/client.dart';

class SDriverVerificationRepository {
  const SDriverVerificationRepository();

  Future<SVerificationStatusResponse> getMyVerificationStatus({
    SVerificationServiceType? serviceType,
    SVerificationVehicleType? vehicleType,
  }) async {
    final query = <String, String>{
      if (serviceType != null) 'service_type': serviceType.value,
      if (vehicleType != null) 'vehicle_type': vehicleType.value,
    };
    final data = await SHttpClient.get(
      _endpoint('/me', query),
      service: SApiService.verification,
      requiresAuth: true,
    );
    return SVerificationStatusResponse.fromJson(data);
  }

  Future<SReviewSubmissionResponse> submitForReview() async {
    final data = await SHttpClient.post(
      '/submit-review',
      service: SApiService.verification,
      requiresAuth: true,
    );

    return SReviewSubmissionResponse.fromJson(data);
  }

  Future<SDriverVehicleSummaryResponse> getVehicleSummary({
    required SVerificationServiceType serviceType,
  }) async {
    final data = await SHttpClient.get(
      _endpoint(
        '/driver/vehicles/summary',
        {'service_type': serviceType.value},
      ),
      service: SApiService.verification,
      requiresAuth: true,
    );
    return SDriverVehicleSummaryResponse.fromJson(data);
  }

  Future<SDriverVehicleSummaryItem> attachVehicleToService({
    required String vehicleId,
    required SVerificationServiceType serviceType,
  }) async {
    final data = await SHttpClient.post(
      '/driver/vehicles/$vehicleId/services',
      service: SApiService.verification,
      body: {'service_type': serviceType.value},
      requiresAuth: true,
    );
    return SDriverVehicleSummaryItem.fromJson(data);
  }

  Future<SDocumentUploadUrlsResponse> submitCnic(
    SCnicSubmissionRequest request,
  ) {
    return _submitDocuments(
      endpoint: '/driver/cnic',
      body: request.toJson(),
    );
  }

  Future<SDocumentUploadUrlsResponse> submitLicense(
    SDriverLicenseSubmissionRequest request,
  ) {
    return _submitDocuments(
      endpoint: '/driver/license',
      body: request.toJson(),
    );
  }

  Future<SDocumentUploadUrlsResponse> submitSelfie(
    SSelfieSubmissionRequest request,
  ) {
    return _submitDocuments(
      endpoint: '/driver/selfie',
      body: request.toJson(),
    );
  }

  Future<SDocumentUploadUrlsResponse> submitVehicle(
    SVehicleSubmissionRequest request,
  ) {
    return _submitDocuments(
      endpoint: '/driver/vehicle',
      body: request.toJson(),
    );
  }

  Future<void> uploadDocument({
    required SPresignedUrlResponse upload,
    required List<int> bytes,
    String contentType = 'image/jpeg',
  }) async {
    await SHttpClient.putBytesToAbsoluteUrl(
      upload.url,
      bytes: bytes,
      contentType: contentType,
    );
  }

  Future<SDocumentUploadUrlsResponse> _submitDocuments({
    required String endpoint,
    required Map<String, dynamic> body,
  }) async {
    final data = await SHttpClient.post(
      endpoint,
      service: SApiService.verification,
      body: body,
      requiresAuth: true,
    );

    return SDocumentUploadUrlsResponse.fromJson(data);
  }

  String _endpoint(String path, Map<String, String> query) {
    if (query.isEmpty) return path;
    return Uri(path: path, queryParameters: query).toString();
  }
}
