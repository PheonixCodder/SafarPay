import 'package:flutter/material.dart';

import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../common/widgets/images/circular_image.dart';
import '../../../../utils/constants/images.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import 'widgets/profile_menu.dart';
import 'widgets/section_heading.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text(STexts.profileTitle),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(SSizes.defaultSpace),
          child: Column(
            children: [
              SizedBox(
                width: double.infinity,
                child: Column(
                  children: [
                    const SCircularImage(
                      imageUrl: SImages.user,
                      width: 80,
                      height: 80,
                    ),
                    TextButton(
                      onPressed: () {},
                      child: const Text(STexts.changeProfilePicture),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: SSizes.spaceBtwItems / 2),
              const Divider(),
              const SizedBox(height: SSizes.spaceBtwItems),

              const SSectionHeading(
                title: STexts.profileInformation,
                showActionButton: false,
              ),
              const SizedBox(height: SSizes.spaceBtwItems),

              SProfileMenu(
                title: STexts.profileName,
                value: STexts.profileDemoName,
                onPressed: () {},
              ),

              const SizedBox(height: SSizes.spaceBtwItems),
              const Divider(),
              const SizedBox(height: SSizes.spaceBtwItems),

              const SSectionHeading(
                title: STexts.personalInformation,
                showActionButton: false,
              ),
              const SizedBox(height: SSizes.spaceBtwItems),

              SProfileMenu(
                title: STexts.profileEmail,
                value: STexts.profileDemoEmail,
                onPressed: () {},
              ),
              SProfileMenu(
                title: STexts.profilePhoneNumber,
                value: STexts.profileDemoPhone,
                onPressed: () {},
              ),
              SProfileMenu(
                title: STexts.profileGender,
                value: STexts.profileDemoGender,
                onPressed: () {},
              ),
              SProfileMenu(
                title: STexts.profileDateOfBirth,
                value: STexts.profileDemoDateOfBirth,
                onPressed: () {},
              ),
            ],
          ),
        ),
      ),
    );
  }
}
