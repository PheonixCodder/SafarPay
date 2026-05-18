import 'package:client/features/home/screens/home/widgets/appbar.dart';
import 'package:client/features/home/screens/home/widgets/categories.dart';
import 'package:client/features/home/screens/home/widgets/searchbar.dart';
import 'package:client/features/location/screens/ride_search/ride_search_screen.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:iconsax/iconsax.dart';

import 'package:client/utils/constants/sizes.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            Column(
              children: [
                const SHomeAppBar(),
                const SizedBox(height: SSizes.spaceBtwSections),
                SSearchContainer(
                  text: STexts.searchBarText,
                  icon: Iconsax.search_normal,
                  endIcon: Iconsax.arrow_circle_right,
                  onSearchPressed: () => Get.to(
                    () => const RideSearchScreen(),
                  ),
                ),
                const SizedBox(height: SSizes.spaceBtwSections),
                const SHomeCategories(),
                const SizedBox(height: SSizes.spaceBtwSections),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
