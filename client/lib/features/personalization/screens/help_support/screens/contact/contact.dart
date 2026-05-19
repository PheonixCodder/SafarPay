import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../../../../../common/navigation/right_slide_page_route.dart';
import '../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../utils/constants/colors.dart';
import '../../../../../../utils/constants/sizes.dart';
import '../../../../../../utils/constants/texts.dart';
import '../live_chat/live_chat.dart';
import 'widgets/contact_action_card.dart';
import 'widgets/contact_illustration.dart';
import 'widgets/contact_social_row.dart';

class ContactScreen extends StatelessWidget {
  const ContactScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text(STexts.contactTitle),
      ),
      body: SafeArea(
        top: false,
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(
            SSizes.defaultSpace,
            SSizes.md,
            SSizes.defaultSpace,
            SSizes.defaultSpace,
          ),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SContactIllustration(),
                  const SizedBox(height: SSizes.lg),
                  Row(
                    children: [
                      SContactActionCard(
                        icon: Iconsax.call,
                        label: 'Call Us',
                        color: SColors.info,
                        onTap: _launchPhone,
                      ),
                      const SizedBox(width: SSizes.md),
                      SContactActionCard(
                        icon: Iconsax.sms,
                        label: 'Email Us',
                        color: SColors.success,
                        onTap: _launchEmail,
                      ),
                      const SizedBox(width: SSizes.md),
                      SContactActionCard(
                        icon: Iconsax.message_text,
                        label: 'Chat',
                        color: SColors.purple,
                        onTap: () => Navigator.of(context).push(
                          SRightSlidePageRoute(page: const LiveChatScreen()),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: SSizes.lg),
                  Text(
                    'Our social media',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: SColors.pureBlack,
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                  const SizedBox(height: SSizes.sm),
                  SContactSocialRow(
                    label: 'Twitter',
                    mark: 'X',
                    onTap: () => _launchWeb('https://x.com'),
                  ),
                  SContactSocialRow(
                    label: 'Instagram',
                    mark: '◎',
                    onTap: () => _launchWeb('https://instagram.com'),
                  ),
                  SContactSocialRow(
                    label: 'Facebook',
                    mark: 'f',
                    onTap: () => _launchWeb('https://facebook.com'),
                  ),
                  SContactSocialRow(
                    label: 'Linked In',
                    mark: 'in',
                    onTap: () => _launchWeb('https://linkedin.com'),
                  ),
                  SContactSocialRow(
                    label: 'Medium',
                    mark: 'M',
                    onTap: () => _launchWeb('https://medium.com'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  static Future<void> _launchPhone() async {
    await _launchUri(Uri(scheme: 'tel', path: STexts.contactSupportPhone));
  }

  static Future<void> _launchEmail() async {
    await _launchUri(
      Uri(
        scheme: 'mailto',
        path: STexts.contactSupportEmail,
      ),
    );
  }

  static Future<void> _launchWeb(String url) async {
    await _launchUri(Uri.parse(url));
  }

  static Future<void> _launchUri(Uri uri) async {
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }
}
