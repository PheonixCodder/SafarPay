import '../data/driver_verification_demo_data.dart';
import '../models/driver_registration_models.dart';
import '../../../../../utils/constants/api_constants.dart';
import '../../../../../utils/http/client.dart';

class SDriverVerificationRepository {
  const SDriverVerificationRepository();

  static const bool _useDemoMode = true;

  Future<SVerificationStatusResponse> getMyVerificationStatus() async {
    // Backend-offline demo mode:
    // Change `activeDriverVerificationDemoScenario` in
    // `driver_verification_demo_data.dart` to preview each UI state.
    //
    // Restore this HTTP call when the Verification backend is available:
    // final data = await SHttpClient.get(
    //   '/me',
    //   service: SApiService.verification,
    //   requiresAuth: true,
    // );
    final data = _useDemoMode
        ? SDriverVerificationDemoData.activeResponse
        : await SHttpClient.get(
            '/me',
            service: SApiService.verification,
            requiresAuth: true,
          );
    return SVerificationStatusResponse.fromJson(data);
  }

  Future<SReviewSubmissionResponse> submitForReview() async {
    // Backend-offline demo mode:
    //
    // Restore this HTTP call when the Verification backend is available:
    // final data = await SHttpClient.post(
    //   '/submit-review',
    //   service: SApiService.verification,
    //   requiresAuth: true,
    // );
    final data = _useDemoMode
        ? {
            'status': 'UNDER_REVIEW',
            'estimated_time_seconds': 30,
          }
        : await SHttpClient.post(
            '/submit-review',
            service: SApiService.verification,
            requiresAuth: true,
          );

    return SReviewSubmissionResponse.fromJson(data);
  }

  Future<SDocumentUploadUrlsResponse> submitCnic(
    SCnicSubmissionRequest request,
  ) {
    return _submitDocuments(
      endpoint: '/driver/cnic',
      body: request.toJson(),
      demoKeys: const ['id_front', 'id_back'],
    );
  }

  Future<SDocumentUploadUrlsResponse> submitLicense(
    SDriverLicenseSubmissionRequest request,
  ) {
    return _submitDocuments(
      endpoint: '/driver/license',
      body: request.toJson(),
      demoKeys: const ['license_front', 'license_back'],
    );
  }

  Future<SDocumentUploadUrlsResponse> submitSelfie(
    SSelfieSubmissionRequest request,
  ) {
    return _submitDocuments(
      endpoint: '/driver/selfie',
      body: request.toJson(),
      demoKeys: const ['selfie_id'],
    );
  }

  Future<SDocumentUploadUrlsResponse> submitVehicle(
    SVehicleSubmissionRequest request,
  ) {
    return _submitDocuments(
      endpoint: '/driver/vehicle',
      body: request.toJson(),
      demoKeys: const [
        'registration_doc_front',
        'registration_doc_back',
        'vehicle_photo_front',
        'vehicle_photo_back',
      ],
    );
  }

  Future<void> uploadDocument({
    required SPresignedUrlResponse upload,
    required List<int> bytes,
    String contentType = 'image/jpeg',
  }) async {
    if (_useDemoMode || upload.url.startsWith('https://demo-upload.local')) {
      await Future<void>.delayed(const Duration(milliseconds: 250));
      return;
    }

    await SHttpClient.putBytesToAbsoluteUrl(
      upload.url,
      bytes: bytes,
      contentType: contentType,
    );
  }

  Future<SDocumentUploadUrlsResponse> _submitDocuments({
    required String endpoint,
    required Map<String, dynamic> body,
    required List<String> demoKeys,
  }) async {
    final data = _useDemoMode
        ? _demoUploadResponse(demoKeys)
        : await SHttpClient.post(
            endpoint,
            service: SApiService.verification,
            body: body,
            requiresAuth: true,
          );

    return SDocumentUploadUrlsResponse.fromJson(data);
  }

  Map<String, dynamic> _demoUploadResponse(List<String> keys) {
    return {
      'message':
          'Success. Please use these URLs to upload the required documents via PUT requests.',
      'urls': {
        for (final key in keys)
          key: {
            'key': 'demo-user/verification/${key}_demo',
            'url': 'https://demo-upload.local/$key',
          },
      },
    };
  }
}
