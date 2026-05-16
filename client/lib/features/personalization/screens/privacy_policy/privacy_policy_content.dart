import 'package:iconsax/iconsax.dart';

import 'privacy_policy_section.dart';

class SPrivacyPolicyContent {
  SPrivacyPolicyContent._();

  static const List<SPrivacyPolicySection> sections = [
    SPrivacyPolicySection(
      icon: Iconsax.document_text,
      title: 'Information we collect',
      summary: 'Account details, contact information, and app activity.',
      body:
          'We collect the information needed to create and secure your SafarPay account, including your name, phone number, email address, profile details, device information, and app activity. We also collect ride-related information when you search, request, schedule, or complete a trip.',
    ),
    SPrivacyPolicySection(
      icon: Iconsax.route_square,
      title: 'Location and ride safety data',
      summary: 'Pickup, dropoff, route, and live trip context.',
      body:
          'SafarPay uses location data to suggest nearby services, estimate routes, connect riders with drivers, support live ride tracking, and help resolve safety or support issues. Location access may be used while a ride flow is active and only for product, safety, support, and compliance purposes.',
    ),
    SPrivacyPolicySection(
      icon: Iconsax.wallet_3,
      title: 'Payments and transactions',
      summary: 'Payment method metadata and transaction records.',
      body:
          'We use payment information to process rides, refunds, promotions, and billing support. Sensitive card or wallet details are handled by payment providers where applicable. SafarPay keeps transaction records needed for receipts, dispute handling, fraud prevention, and legal obligations.',
    ),
    SPrivacyPolicySection(
      icon: Iconsax.shield_tick,
      title: 'How we use information',
      summary: 'Reliability, safety, support, and personalization.',
      body:
          'Your information helps us authenticate users, operate ride services, improve pickup accuracy, notify you about trip updates, prevent misuse, personalize the app experience, and provide customer support. We do not sell personal information.',
    ),
    SPrivacyPolicySection(
      icon: Iconsax.profile_2user,
      title: 'Sharing and service providers',
      summary: 'Drivers, support teams, infrastructure, and compliance.',
      body:
          'We share limited information with drivers, payment processors, verification providers, infrastructure partners, analytics providers, support teams, and authorities when required by law. Each sharing path is limited to what is needed for the service or obligation.',
    ),
    SPrivacyPolicySection(
      icon: Iconsax.archive_tick,
      title: 'Retention and deletion',
      summary: 'Stored only while needed for service and legal reasons.',
      body:
          'We retain account, ride, payment, safety, and support records for as long as needed to provide SafarPay, comply with legal requirements, resolve disputes, prevent fraud, and enforce our terms. You can request deletion where legally available.',
    ),
    SPrivacyPolicySection(
      icon: Iconsax.setting_2,
      title: 'Your choices and controls',
      summary: 'Manage profile, permissions, and communication choices.',
      body:
          'You can update profile information, manage device permissions, adjust notification preferences, and contact support about account or privacy requests. Some permissions may be required for core ride features to work correctly.',
    ),
    SPrivacyPolicySection(
      icon: Iconsax.refresh_circle,
      title: 'Policy updates',
      summary: 'Important changes will be reflected in the app.',
      body:
          'We may update this policy as SafarPay grows. When changes are meaningful, we will update the effective date and may notify you through the app or other contact channels before the changes take effect.',
    ),
  ];
}
