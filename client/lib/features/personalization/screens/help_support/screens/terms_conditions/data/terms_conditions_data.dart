import 'package:iconsax/iconsax.dart';

import '../models/terms_policy.dart';

class STermsConditionsData {
  STermsConditionsData._();

  static const String lastUpdated = 'May 15, 2024';

  static const List<STermsPolicy> policies = [
    STermsPolicy(
      id: 'rider-terms',
      title: 'Rider Terms of Service',
      subtitle: 'Rules and guidelines for riders',
      icon: Iconsax.user,
      lastUpdated: lastUpdated,
      sections: [
        STermsPolicySection(
          title: 'Acceptance of Terms',
          body:
              'By using SafarPay, you agree to follow these rider terms and any service rules shown during booking, payment, pickup, and trip completion.',
        ),
        STermsPolicySection(
          title: 'Use of the Service',
          body:
              'You may request rides, courier services, freight support, or other available mobility services only for lawful and accurate purposes.',
        ),
        STermsPolicySection(
          title: 'User Responsibilities',
          body:
              'You are responsible for accurate pickup and dropoff details, respectful conduct, safe boarding, and keeping your account information current.',
        ),
        STermsPolicySection(
          title: 'Payments & Fees',
          body:
              'Fares, offers, fees, tolls, cancellation charges, and promotions may apply based on the selected service and confirmed ride details.',
        ),
        STermsPolicySection(
          title: 'Cancellations & Refunds',
          body:
              'Cancellation and refund eligibility depends on ride status, driver progress, payment method, and the refund policy shown in the app.',
        ),
        STermsPolicySection(
          title: 'Prohibited Conduct',
          body:
              'Fraud, harassment, unsafe behavior, false bookings, payment abuse, and attempts to misuse driver or platform systems are not allowed.',
        ),
        STermsPolicySection(
          title: 'Limitation of Liability',
          body:
              'SafarPay works to provide reliable services, but availability, route conditions, pricing estimates, and third-party service performance may vary.',
        ),
      ],
    ),
    STermsPolicy(
      id: 'driver-terms',
      title: 'Driver Terms of Service',
      subtitle: 'Rules and guidelines for drivers',
      icon: Iconsax.car,
      lastUpdated: lastUpdated,
      sections: [
        STermsPolicySection(
          title: 'Driver Eligibility',
          body:
              'Drivers must maintain approved identity, license, vehicle, and safety verification before accepting trips through SafarPay.',
        ),
        STermsPolicySection(
          title: 'Service Standards',
          body:
              'Drivers should keep vehicles clean, arrive safely, follow the agreed route context, and treat riders and packages with care.',
        ),
        STermsPolicySection(
          title: 'Trip Acceptance',
          body:
              'Accepted trips, bids, counter-offers, and fixed fares should be honored unless cancellation is necessary for safety or platform-supported reasons.',
        ),
        STermsPolicySection(
          title: 'Payments & Settlements',
          body:
              'Driver payouts, deductions, incentives, refunds, and settlement timing depend on completed ride records and account status.',
        ),
        STermsPolicySection(
          title: 'Safety Requirements',
          body:
              'Drivers must follow traffic laws, avoid unsafe driving, and cooperate with support when a trip, incident, or verification review requires attention.',
        ),
      ],
    ),
    STermsPolicy(
      id: 'privacy-policy',
      title: 'Privacy Policy',
      subtitle: 'How we collect and use your data',
      icon: Iconsax.shield_tick,
      lastUpdated: lastUpdated,
      sections: [
        STermsPolicySection(
          title: 'Information We Collect',
          body:
              'SafarPay may collect account, contact, location, trip, payment, device, and support information needed to operate mobility services.',
        ),
        STermsPolicySection(
          title: 'How We Use Information',
          body:
              'We use information to match rides, calculate routes and prices, process payments, support safety, prevent abuse, and improve the app.',
        ),
        STermsPolicySection(
          title: 'Location Data',
          body:
              'Location data supports pickup, dropoff, routing, live trip tracking, driver matching, service availability, and safety review workflows.',
        ),
        STermsPolicySection(
          title: 'Data Sharing',
          body:
              'Relevant trip and account details may be shared with riders, drivers, payment providers, support teams, and legal authorities when required.',
        ),
        STermsPolicySection(
          title: 'Data Controls',
          body:
              'Users can update account details and communication preferences in the app where supported. Some records may be retained for safety and legal needs.',
        ),
      ],
    ),
    STermsPolicy(
      id: 'refund-policy',
      title: 'Refund Policy',
      subtitle: 'How refunds are processed',
      icon: Iconsax.refresh_circle,
      lastUpdated: lastUpdated,
      sections: [
        STermsPolicySection(
          title: 'Refund Eligibility',
          body:
              'Refunds may be reviewed for duplicate payments, eligible cancellations, service failures, incorrect charges, or support-approved disputes.',
        ),
        STermsPolicySection(
          title: 'Cancellation Charges',
          body:
              'A cancellation charge may apply when a driver has already accepted, traveled, arrived, or waited according to the ride state.',
        ),
        STermsPolicySection(
          title: 'Processing Time',
          body:
              'Approved refunds are processed to the original payment method or wallet where supported. Bank and provider timelines may vary.',
        ),
        STermsPolicySection(
          title: 'Dispute Review',
          body:
              'Support may use ride status, GPS events, payment records, communication records, and platform logs to review a refund request.',
        ),
      ],
    ),
    STermsPolicy(
      id: 'community-guidelines',
      title: 'Community Guidelines',
      subtitle: 'Our community standards',
      icon: Iconsax.profile_2user,
      lastUpdated: lastUpdated,
      sections: [
        STermsPolicySection(
          title: 'Respectful Conduct',
          body:
              'Riders, drivers, and support teams are expected to communicate respectfully and avoid harassment, threats, discrimination, or abuse.',
        ),
        STermsPolicySection(
          title: 'Safe Trips',
          body:
              'Everyone should support safe pickup, travel, delivery, loading, unloading, and ride completion behavior.',
        ),
        STermsPolicySection(
          title: 'Platform Integrity',
          body:
              'Fake accounts, manipulated trips, fraudulent payments, false reports, or attempts to bypass SafarPay systems are not permitted.',
        ),
        STermsPolicySection(
          title: 'Reporting Issues',
          body:
              'Users should report safety issues, payment disputes, misconduct, or suspicious activity through support as soon as possible.',
        ),
      ],
    ),
    STermsPolicy(
      id: 'safety-liability',
      title: 'Safety & Liability',
      subtitle: 'Important information',
      icon: Iconsax.security_safe,
      lastUpdated: lastUpdated,
      sections: [
        STermsPolicySection(
          title: 'Safety First',
          body:
              'Use SafarPay only when it is safe to do so. Riders and drivers should follow local laws and avoid unsafe pickup or dropoff choices.',
        ),
        STermsPolicySection(
          title: 'Emergency Situations',
          body:
              'In emergencies, contact local emergency services first. SafarPay support may help with platform records after immediate safety needs are handled.',
        ),
        STermsPolicySection(
          title: 'Service Availability',
          body:
              'Service availability can depend on drivers, location, demand, weather, network access, regulations, and other operational conditions.',
        ),
        STermsPolicySection(
          title: 'Liability Limits',
          body:
              'SafarPay is not responsible for losses outside the platform service scope except where required by applicable law.',
        ),
      ],
    ),
  ];

  static STermsPolicy policyById(String id) {
    return policies.firstWhere((policy) => policy.id == id);
  }
}
