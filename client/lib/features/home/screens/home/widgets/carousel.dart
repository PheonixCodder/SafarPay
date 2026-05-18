import 'package:carousel_slider/carousel_slider.dart';
import 'package:client/common/widgets/images/rounded_image.dart';
import 'package:client/utils/constants/images.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:flutter/material.dart';

class SHomeSlider extends StatelessWidget {
  const SHomeSlider({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        CarouselSlider(
          options: CarouselOptions(
            height: SSizes.imageCarouselHeight,
            viewportFraction: 1,
          ),
          items: const [
            SRoundedImage(
              imageUrl: SImages.banner1,
              padding: EdgeInsets.symmetric(
                horizontal: SSizes.imageCarouselHorizontalPadding,
              ),
            ),
            SRoundedImage(
              imageUrl: SImages.banner2,
              padding: EdgeInsets.symmetric(
                horizontal: SSizes.imageCarouselHorizontalPadding,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
