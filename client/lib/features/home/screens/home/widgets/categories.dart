import 'package:client/common/navigation/right_slide_page_route.dart';
import 'package:client/features/location/domain/ride_booking_models.dart';
import 'package:client/features/location/screens/ride_search/ride_search_screen.dart';
import 'package:client/utils/constants/colors.dart';
import 'package:client/utils/constants/images.dart';
import 'package:client/utils/constants/sizes.dart';
import 'package:client/utils/constants/texts.dart';
import 'package:client/utils/helpers/helpers.dart';
import 'package:flutter/material.dart';
import 'category_tile.dart';

class SHomeCategories extends StatelessWidget {
  const SHomeCategories({super.key});

  void _openCategory(
      BuildContext context,
      SPassengerServiceCategory category,
      ) {
    Navigator.of(context).push(
      SRightSlidePageRoute(
        page: RideSearchScreen(initialCategory: category),
      ),
    );
  }

  // Define the explore action here
  void _onExplorePressed(BuildContext context) {
    Navigator.of(context).push(
      SRightSlidePageRoute(
        page: RideSearchScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    const gap = SSizes.md;
    final textTheme = Theme.of(context).textTheme;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: SSizes.lg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  STexts.categories,
                  style: textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                    color: SColors.textPrimary,
                    letterSpacing: SSizes.homeCategoryTitleLetterSpacing,
                  ),
                ),
              ),
              // Added Material and InkWell for tap functionality with splash effect
              Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: () => _onExplorePressed(context),
                  borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: SSizes.md,
                      vertical: SSizes.sm,
                    ),
                    decoration: BoxDecoration(
                      color: SHelperFunctions.withOpacity(
                        SColors.primary,
                        SOpacities.tinted,
                      ),
                      borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
                    ),
                    child: Text(
                      STexts.categoriesExplore,
                      style: textTheme.labelMedium?.copyWith(
                        color: SColors.primary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: SSizes.lg),

          /// TOP GRID
          SizedBox(
            height: SSizes.homeCategoryTopGridHeight,
            child: Row(
              children: [
                Expanded(
                  flex: 6,
                  child: SCategoryTile(
                    title: STexts.groceries,
                    subtitle: STexts.groceriesEta,
                    image: SImages.groceries,
                    isLarge: true,
                    showBadge: true,
                    onTap: () => _openCategory(
                      context,
                      SPassengerServiceCategory.groceries,
                    ),
                  ),
                ),
                const SizedBox(width: gap),
                Expanded(
                  flex: 4,
                  child: Column(
                    children: [
                      Expanded(
                        child: SCategoryTile(
                          title: STexts.cityRides,
                          image: SImages.cityRides,
                          onTap: () => _openCategory(
                            context,
                            SPassengerServiceCategory.cityRides,
                          ),
                        ),
                      ),
                      const SizedBox(height: gap),
                      Expanded(
                        child: SCategoryTile(
                          title: STexts.cityToCity,
                          image: SImages.cityToCity,
                          onTap: () => _openCategory(
                            context,
                            SPassengerServiceCategory.cityToCity,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: gap),

          /// BOTTOM GRID
          SizedBox(
            height: SSizes.homeCategoryBottomGridHeight,
            child: Row(
              children: [
                Expanded(
                  child: SCategoryTile(
                    title: STexts.courier,
                    image: SImages.courier,
                    onTap: () => _openCategory(
                      context,
                      SPassengerServiceCategory.courier,
                    ),
                  ),
                ),
                const SizedBox(width: gap),
                Expanded(
                  child: SCategoryTile(
                    title: STexts.freight,
                    image: SImages.freight,
                    onTap: () => _openCategory(
                      context,
                      SPassengerServiceCategory.freight,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
