import 'package:flutter/material.dart';

class SCircularImage extends StatelessWidget {
  const SCircularImage({
    super.key,
    this.width = 56,
    this.height = 56,
    required this.imageUrl,
    this.border,
    this.backgroundColor = Colors.transparent,
    this.fit,
    this.padding,
    this.isNetworkImage = false,
    this.onPressed,
  });

  final double? width, height;
  final String imageUrl;
  final BoxBorder? border;
  final Color backgroundColor;
  final BoxFit? fit;
  final EdgeInsetsGeometry? padding;
  final bool isNetworkImage;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    final ImageProvider<Object> imageProvider =
    isNetworkImage
        ? NetworkImage(imageUrl) as ImageProvider<Object>
        : AssetImage(imageUrl) as ImageProvider<Object>;

    return GestureDetector(
      onTap: onPressed,
      child: Container(
        width: width,
        height: height,
        padding: padding,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: border,
          color: backgroundColor,
        ),
        child: ClipOval(
          child: Image(
            image: imageProvider,
            fit: fit ?? BoxFit.cover,
            width: width,
            height: height,
          ),
        ),
      ),
    );
  }
}