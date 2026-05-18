import 'package:camera/camera.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

class SSelfieLiveCamera extends StatelessWidget {
  const SSelfieLiveCamera({
    super.key,
    required this.isInitializingCamera,
    required this.cameraController,
  });

  final bool isInitializingCamera;
  final CameraController? cameraController;

  @override
  Widget build(BuildContext context) {
    if (isInitializingCamera) {
      return const Center(
        child: CircularProgressIndicator(color: SColors.primary),
      );
    }
    if (cameraController == null || !cameraController!.value.isInitialized) {
      return const Center(
        child: Icon(Iconsax.camera_slash, color: SColors.white),
      );
    }

    return CameraPreview(cameraController!);
  }
}
