import 'package:client/features/home/screens/widgets/appbar.dart';
import 'package:client/features/home/screens/widgets/carousel.dart';
import 'package:client/features/home/screens/widgets/categories.dart';
import 'package:client/features/home/screens/widgets/searchbar.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../utils/constants/sizes.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: const [
            Column(
              children: [
                SHomeAppBar(),
                SizedBox(height: SSizes.spaceBtwSections),
                SSearchContainer(
                  text: STexts.searchBarText,
                  icon: Iconsax.search_normal,
                  endIcon: Iconsax.arrow_circle_right,
                ),
                SizedBox(height: SSizes.spaceBtwSections),
                SHomeCategories(),
                SizedBox(height: SSizes.spaceBtwSections),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
