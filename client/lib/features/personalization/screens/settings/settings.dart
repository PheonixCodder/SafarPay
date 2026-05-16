import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../common/navigation/right_slide_page_route.dart';
import '../../../../common/widgets/appbar/appbar.dart';
import '../../../../common/widgets/containers/primary_header_container.dart';
import '../../../../utils/constants/colors.dart';
import '../../../../utils/constants/sizes.dart';
import '../../../../utils/constants/texts.dart';
import '../../models/settings_menu_item.dart';
import '../help_support/help_support.dart';
import '../notifications/notifications.dart';
import '../privacy_policy/privacy_policy.dart';
import '../profile/profile.dart';
import 'widgets/settings_list.dart';
import 'widgets/settings_logout_button.dart';
import 'widgets/settings_profile_tile.dart';
import 'widgets/settings_section_heading.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  static const List<SSettingsMenuItem> _accountSettings = [
    SSettingsMenuItem(
      icon: Iconsax.user,
      title: STexts.userInfo,
      subtitle: STexts.userInfoSubTitle,
    ),
    SSettingsMenuItem(
      icon: Iconsax.bank,
      title: STexts.settingsPayments,
      subtitle: STexts.settingsPaymentsSubTitle,
    ),
    SSettingsMenuItem(
      icon: Iconsax.notification,
      title: STexts.settingsNotifications,
      subtitle: STexts.settingsNotificationsSubTitle,
    ),
    SSettingsMenuItem(
      icon: Iconsax.personalcard,
      title: STexts.driver,
      subtitle: STexts.driverSubTitle,
    ),
  ];

  static const List<SSettingsMenuItem> _appSettings = [
    SSettingsMenuItem(
      icon: Iconsax.security,
      title: STexts.settingsPrivacySecurity,
      subtitle: STexts.settingsPrivacySecuritySubTitle,
    ),
    SSettingsMenuItem(
      icon: Iconsax.support,
      title: STexts.settingsSupport,
      subtitle: STexts.settingsSupportSubTitle,
    ),
  ];

  void _openProfileScreen(BuildContext context) {
    Navigator.of(context).push(
      SRightSlidePageRoute(page: const ProfileScreen()),
    );
  }

  void _openPrivacyPolicyScreen(BuildContext context) {
    Navigator.of(context).push(
      SRightSlidePageRoute(page: const PrivacyPolicyScreen()),
    );
  }

  void _openNotificationsScreen(BuildContext context) {
    Navigator.of(context).push(
      SRightSlidePageRoute(page: const NotificationsScreen()),
    );
  }

  void _openHelpSupportScreen(BuildContext context) {
    Navigator.of(context).push(
      SRightSlidePageRoute(page: const HelpSupportScreen()),
    );
  }

  VoidCallback? _accountItemAction(
    BuildContext context,
    SSettingsMenuItem item,
    int index,
  ) {
    if (index == 0 && item.title == STexts.userInfo) {
      return () => _openProfileScreen(context);
    }
    if (index == 2 && item.title == STexts.settingsNotifications) {
      return () => _openNotificationsScreen(context);
    }
    return null;
  }

  VoidCallback? _appItemAction(
    BuildContext context,
    SSettingsMenuItem item,
    int index,
  ) {
    if (index == 0 && item.title == STexts.settingsPrivacySecurity) {
      return () => _openPrivacyPolicyScreen(context);
    }
    if (index == 1 && item.title == STexts.settingsSupport) {
      return () => _openHelpSupportScreen(context);
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            SPrimaryHeaderContainer(
              child: Column(
                children: [
                  SAppBar(
                    title: Text(
                      STexts.settingsAccount,
                      style:
                          Theme.of(context).textTheme.headlineMedium?.copyWith(
                                color: SColors.white,
                              ),
                    ),
                  ),
                  const SizedBox(height: SSizes.spaceBtwSections),
                  SSettingsProfileTile(
                    onEdit: () => _openProfileScreen(context),
                  ),
                  const SizedBox(height: SSizes.spaceBtwSections),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(SSizes.defaultSpace),
              child: Column(
                children: [
                  const SSettingsSectionHeading(title: STexts.accountSettings),
                  const SizedBox(height: SSizes.spaceBtnItems),
                  SSettingsList(
                    items: _accountSettings,
                    onItemTap: (item, index) =>
                        _accountItemAction(context, item, index),
                  ),
                  const SizedBox(height: SSizes.spaceBtwSections),
                  const SSettingsSectionHeading(title: STexts.appSettings),
                  const SizedBox(height: SSizes.spaceBtnItems),
                  SSettingsList(
                    items: _appSettings,
                    onItemTap: (item, index) =>
                        _appItemAction(context, item, index),
                  ),
                  const SizedBox(height: SSizes.spaceBtwSections),
                  const SSettingsLogoutButton(),
                  const SizedBox(height: SSizes.spaceBtwSections),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
