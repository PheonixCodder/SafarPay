import 'package:flutter/material.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';

class SRoundedImage extends StatelessWidget {
  const SRoundedImage({
    super.key,
    required this.imageUrl,
    this.width = double.infinity,
    this.height = SSizes.imageCarouselHeight,
    this.applyImageRadius = true,
    this.border,
    this.backgroundColor = SColors.transparent,
    this.fit = BoxFit.cover,
    this.padding,
    this.isNetworkImage = false,
    this.onPressed,
    this.borderRadius = SSizes.cardRadiusLg,
  });

  final double? width;
  final double? height;
  final String imageUrl;
  final bool applyImageRadius;
  final BoxBorder? border;
  final Color backgroundColor;
  final BoxFit? fit;
  final EdgeInsetsGeometry? padding;
  final bool isNetworkImage;
  final VoidCallback? onPressed;
  final double borderRadius;

  @override
  Widget build(BuildContext context) {
    final ImageProvider<Object> imageProvider;
    if (isNetworkImage) {
      imageProvider = NetworkImage(imageUrl);
    } else {
      imageProvider = AssetImage(imageUrl);
    }

    return GestureDetector(
      onTap: onPressed,
      child: Container(
        width: width,
        height: height,
        padding: padding,
        decoration: BoxDecoration(
          border: border,
          color: backgroundColor,
          borderRadius: BorderRadius.circular(borderRadius),
        ),
        child: ClipRRect(
          borderRadius: applyImageRadius
              ? BorderRadius.circular(borderRadius)
              : BorderRadius.zero,
          child: Image(
            fit: fit,
            image: imageProvider,
          ),
        ),
      ),
    );
  }
}
