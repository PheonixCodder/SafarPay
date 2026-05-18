import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:image_picker/image_picker.dart';

import '../../../../../utils/validators/validator.dart';
import '../models/driver_registration_models.dart';
import '../repositories/driver_verification_repository.dart';

class SCnicRegistrationController extends GetxController {
  SCnicRegistrationController({
    SDriverVerificationRepository repository =
        const SDriverVerificationRepository(),
    ImagePicker? imagePicker,
  })  : _repository = repository,
        _imagePicker = imagePicker ?? ImagePicker();

  final SDriverVerificationRepository _repository;
  final ImagePicker _imagePicker;
  final formKey = GlobalKey<FormState>();
  final idNumberController = TextEditingController();
  final Rxn<DateTime> expiryDate = Rxn<DateTime>();
  final Rxn<XFile> frontImage = Rxn<XFile>();
  final Rxn<XFile> backImage = Rxn<XFile>();
  final RxBool isSubmitting = false.obs;
  final RxnString errorMessage = RxnString();

  String? get expiryError =>
      SValidator.validateFutureDate(expiryDate.value, fieldName: 'CNIC expiry');

  bool get hasAllImages => frontImage.value != null && backImage.value != null;

  Future<void> pickFront(ImageSource source) => _pickImage(source, frontImage);

  Future<void> pickBack(ImageSource source) => _pickImage(source, backImage);

  void removeFront() => frontImage.value = null;

  void removeBack() => backImage.value = null;

  Future<bool> submit() async {
    errorMessage.value = null;
    final isValid = formKey.currentState?.validate() ?? false;
    final dateError = expiryError;

    if (!isValid || dateError != null) {
      errorMessage.value = dateError ?? 'Please check your CNIC details.';
      return false;
    }
    if (!hasAllImages) {
      errorMessage.value = 'Upload front and back CNIC images.';
      return false;
    }

    isSubmitting.value = true;
    try {
      final response = await _repository.submitCnic(
        SCnicSubmissionRequest(
          idNumber: idNumberController.text.trim(),
          expiryDate: expiryDate.value!,
        ),
      );

      await _upload(response, 'id_front', frontImage.value!);
      await _upload(response, 'id_back', backImage.value!);
      return true;
    } catch (error) {
      errorMessage.value = error.toString();
      return false;
    } finally {
      isSubmitting.value = false;
    }
  }

  Future<void> _pickImage(ImageSource source, Rxn<XFile> target) async {
    final image = await _imagePicker.pickImage(
      source: source,
      imageQuality: 85,
      maxWidth: 1800,
    );
    if (image != null) target.value = image;
  }

  Future<void> _upload(
    SDocumentUploadUrlsResponse response,
    String key,
    XFile image,
  ) async {
    final upload = response.urls[key];
    if (upload == null) {
      throw Exception('Upload URL missing for $key.');
    }

    await _repository.uploadDocument(
      upload: upload,
      bytes: await image.readAsBytes(),
    );
  }

  @override
  void onClose() {
    idNumberController.dispose();
    super.onClose();
  }
}
