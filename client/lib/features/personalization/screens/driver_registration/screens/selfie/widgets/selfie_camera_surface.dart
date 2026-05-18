import 'dart:io';

import 'package:camera/camera.dart';
import 'package:client/features/personalization/screens/driver_registration/screens/selfie/widgets/selfie_live_camera.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';

class SSelfieCameraSurface extends StatelessWidget {
  const SSelfieCameraSurface({
    super.key,
    required this.capturedImage,
    required this.isInitializingCamera,
    required this.cameraController,
  });

  final XFile? capturedImage;
  final bool isInitializingCamera;
  final CameraController? cameraController;

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
      child: AspectRatio(
        aspectRatio: 3 / 4,
        child: Container(
          color: SColors.black,
          child: capturedImage != null
              ? Image.file(File(capturedImage!.path), fit: BoxFit.cover)
              : SSelfieLiveCamera(
                  isInitializingCamera: isInitializingCamera,
                  cameraController: cameraController,
                ),
        ),
      ),
    );
  }
}
