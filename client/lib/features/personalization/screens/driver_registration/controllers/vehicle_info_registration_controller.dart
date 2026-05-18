import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:image_picker/image_picker.dart';

import '../models/driver_registration_models.dart';
import '../repositories/driver_verification_repository.dart';

class SVehicleInfoRegistrationController extends GetxController {
  SVehicleInfoRegistrationController({
    required SDriverVehicleOption vehicle,
    SDriverVerificationRepository repository =
        const SDriverVerificationRepository(),
    ImagePicker? imagePicker,
  })  : selectedVehicleType =
            SVerificationVehicleType.fromDisplayVehicle(vehicle.type).obs,
        _repository = repository,
        _imagePicker = imagePicker ?? ImagePicker();

  final SDriverVerificationRepository _repository;
  final ImagePicker _imagePicker;
  final formKey = GlobalKey<FormState>();
  final brandController = TextEditingController();
  final modelController = TextEditingController();
  final colorController = TextEditingController();
  final passengersController = TextEditingController(text: '4');
  final plateNumberController = TextEditingController();
  final productionYearController = TextEditingController();
  final Rx<SVerificationVehicleType> selectedVehicleType;
  final Rxn<XFile> registrationFrontImage = Rxn<XFile>();
  final Rxn<XFile> registrationBackImage = Rxn<XFile>();
  final Rxn<XFile> vehicleFrontImage = Rxn<XFile>();
  final Rxn<XFile> vehicleBackImage = Rxn<XFile>();
  final RxBool isSubmitting = false.obs;
  final RxnString errorMessage = RxnString();

  bool get hasAllImages =>
      registrationFrontImage.value != null &&
      registrationBackImage.value != null &&
      vehicleFrontImage.value != null &&
      vehicleBackImage.value != null;

  Future<void> pickRegistrationFront(ImageSource source) =>
      _pickImage(source, registrationFrontImage);

  Future<void> pickRegistrationBack(ImageSource source) =>
      _pickImage(source, registrationBackImage);

  Future<void> pickVehicleFront(ImageSource source) =>
      _pickImage(source, vehicleFrontImage);

  Future<void> pickVehicleBack(ImageSource source) =>
      _pickImage(source, vehicleBackImage);

  Future<bool> submit() async {
    errorMessage.value = null;
    final isValid = formKey.currentState?.validate() ?? false;
    if (!isValid) {
      errorMessage.value = 'Please check your vehicle details.';
      return false;
    }
    if (!hasAllImages) {
      errorMessage.value = 'Upload all required vehicle documents and photos.';
      return false;
    }

    isSubmitting.value = true;
    try {
      final response = await _repository.submitVehicle(
        SVehicleSubmissionRequest(
          brand: brandController.text.trim(),
          model: modelController.text.trim(),
          color: colorController.text.trim(),
          vehicleType: selectedVehicleType.value,
          maxPassengers: int.parse(passengersController.text.trim()),
          plateNumber: plateNumberController.text.trim(),
          productionYear: int.parse(productionYearController.text.trim()),
        ),
      );

      await _upload(
        response,
        'registration_doc_front',
        registrationFrontImage.value!,
      );
      await _upload(
        response,
        'registration_doc_back',
        registrationBackImage.value!,
      );
      await _upload(response, 'vehicle_photo_front', vehicleFrontImage.value!);
      await _upload(response, 'vehicle_photo_back', vehicleBackImage.value!);
      return true;
    } catch (error) {
      errorMessage.value = error.toString();
      return false;
    } finally {
      isSubmitting.value = false;
    }
  }

  void removeRegistrationFront() => registrationFrontImage.value = null;

  void removeRegistrationBack() => registrationBackImage.value = null;

  void removeVehicleFront() => vehicleFrontImage.value = null;

  void removeVehicleBack() => vehicleBackImage.value = null;

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
    brandController.dispose();
    modelController.dispose();
    colorController.dispose();
    passengersController.dispose();
    plateNumberController.dispose();
    productionYearController.dispose();
    super.onClose();
  }
}
