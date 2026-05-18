import 'package:camera/camera.dart';
import 'package:get/get.dart';

import '../models/driver_registration_models.dart';
import '../repositories/driver_verification_repository.dart';

class SSelfieWithLicenseController extends GetxController {
  SSelfieWithLicenseController({
    SDriverVerificationRepository repository =
        const SDriverVerificationRepository(),
  }) : _repository = repository;

  final SDriverVerificationRepository _repository;
  final RxBool isInitializingCamera = true.obs;
  final RxBool isSubmitting = false.obs;
  final RxnString errorMessage = RxnString();
  final Rxn<XFile> capturedImage = Rxn<XFile>();
  CameraController? cameraController;

  Future<void> initializeCamera() async {
    isInitializingCamera.value = true;
    errorMessage.value = null;

    try {
      final cameras = await availableCameras();
      final camera = cameras.firstWhere(
        (item) => item.lensDirection == CameraLensDirection.front,
        orElse: () => cameras.first,
      );
      cameraController = CameraController(
        camera,
        ResolutionPreset.medium,
        enableAudio: false,
      );
      await cameraController!.initialize();
    } catch (error) {
      errorMessage.value = 'Camera unavailable. Please try again.';
    } finally {
      isInitializingCamera.value = false;
    }
  }

  Future<void> capture() async {
    final controller = cameraController;
    if (controller == null || !controller.value.isInitialized) return;

    try {
      capturedImage.value = await controller.takePicture();
    } catch (error) {
      errorMessage.value = 'Could not capture selfie. Please retry.';
    }
  }

  void retry() => capturedImage.value = null;

  Future<bool> submit() async {
    final image = capturedImage.value;
    if (image == null) {
      errorMessage.value = 'Capture your selfie with license first.';
      return false;
    }

    isSubmitting.value = true;
    errorMessage.value = null;

    try {
      final response = await _repository.submitSelfie(
        const SSelfieSubmissionRequest(),
      );
      final upload = response.urls['selfie_id'];
      if (upload == null) {
        throw Exception('Upload URL missing for selfie_id.');
      }

      await _repository.uploadDocument(
        upload: upload,
        bytes: await image.readAsBytes(),
      );
      return true;
    } catch (error) {
      errorMessage.value = error.toString();
      return false;
    } finally {
      isSubmitting.value = false;
    }
  }

  @override
  void onClose() {
    cameraController?.dispose();
    super.onClose();
  }
}
