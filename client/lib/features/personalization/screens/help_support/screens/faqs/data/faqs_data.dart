import 'package:iconsax/iconsax.dart';

import '../models/faq_models.dart';

class SFaqsData {
  SFaqsData._();

  static const List<SFaqCategory> categories = [
    SFaqCategory(
      id: 'rider',
      title: 'Rider',
      subtitle: 'Everything about riding and trips',
      icon: Iconsax.car,
    ),
    SFaqCategory(
      id: 'payments',
      title: 'Payments',
      subtitle: 'Payments, refunds and wallet',
      icon: Iconsax.card,
    ),
    SFaqCategory(
      id: 'safety',
      title: 'Safety',
      subtitle: 'Safety tools and reporting issues',
      icon: Iconsax.shield_tick,
    ),
    SFaqCategory(
      id: 'account',
      title: 'Account',
      subtitle: 'Account, profile and verification',
      icon: Iconsax.user,
    ),
    SFaqCategory(
      id: 'technical',
      title: 'Technical',
      subtitle: 'App issues and troubleshooting',
      icon: Iconsax.setting_2,
    ),
    SFaqCategory(
      id: 'driver',
      title: 'Driver',
      subtitle: 'Information for drivers',
      icon: Iconsax.profile_2user,
    ),
  ];

  static const List<SFaqArticle> popularArticles = [
    SFaqArticle(
      id: 'cancel-ride',
      categoryId: 'rider',
      title: 'How do I cancel a ride?',
      summary:
          'You can cancel a ride from the active ride screen before the trip is completed.',
      sectionTitle: 'Before you cancel',
      bullets: [
        'Open the active ride screen',
        'Tap cancel ride',
        'Choose the reason that best fits',
        'Confirm cancellation',
      ],
      highlightTitle: 'Cancellation notice',
      highlightBody:
          'A cancellation fee may apply if the driver has already accepted or arrived.',
      relatedArticleIds: ['cancellation-fee', 'refunds-work'],
    ),
    SFaqArticle(
      id: 'refunds-work',
      categoryId: 'payments',
      title: 'How do refunds work?',
      summary:
          'Refunds are issued for eligible cancelled rides, payment failures, or overcharged amounts.',
      sectionTitle: 'When am I eligible for a refund?',
      bullets: [
        'Driver canceled the ride',
        'Double payment deducted',
        'Overcharge or incorrect fare',
        'Payment failure but amount deducted',
      ],
      highlightTitle: 'Refund Timelines',
      highlightBody:
          'Refunds are usually processed within 3-5 business days depending on your payment method.',
      relatedArticleIds: ['cancel-ride', 'cancellation-fee'],
    ),
    SFaqArticle(
      id: 'cancellation-fee',
      categoryId: 'payments',
      title: 'What is a cancellation fee?',
      summary:
          'A cancellation fee helps compensate a driver when they have already accepted, traveled, or waited for a trip.',
      sectionTitle: 'When can a fee apply?',
      bullets: [
        'Driver has already accepted the ride',
        'Driver is close to pickup',
        'Driver has waited at pickup',
        'Repeated late cancellations are detected',
      ],
      highlightTitle: 'Fee review',
      highlightBody:
          'If you believe a fee was applied incorrectly, contact support with the ride details.',
      relatedArticleIds: ['cancel-ride', 'refunds-work'],
    ),
    SFaqArticle(
      id: 'change-payment-method',
      categoryId: 'payments',
      title: 'How do I change my payment method?',
      summary:
          'Payment methods can be changed before confirming a ride where supported by the service.',
      sectionTitle: 'Steps to change payment',
      bullets: [
        'Open payment options before confirming',
        'Choose wallet, cash, or saved method',
        'Review the fare summary',
        'Confirm the ride',
      ],
      highlightTitle: 'Payment availability',
      highlightBody:
          'Some payment methods may not be available for every city, service, or account state.',
      relatedArticleIds: ['refunds-work', 'cancellation-fee'],
    ),
    SFaqArticle(
      id: 'report-driver',
      categoryId: 'safety',
      title: 'How to report a driver?',
      summary:
          'You can report safety, behavior, payment, or route concerns from ride help or support.',
      sectionTitle: 'What to include',
      bullets: [
        'Ride date and route',
        'Driver or vehicle concern',
        'Payment or fare issue',
        'Any urgent safety detail',
      ],
      highlightTitle: 'Safety first',
      highlightBody:
          'If there is immediate danger, contact local emergency services before contacting support.',
      relatedArticleIds: ['lost-item', 'cancel-ride'],
    ),
    SFaqArticle(
      id: 'lost-item',
      categoryId: 'rider',
      title: 'I lost an item in the ride',
      summary:
          'If you left an item in a ride, contact support with your ride details as soon as possible.',
      sectionTitle: 'How to request help',
      bullets: [
        'Open the completed ride details',
        'Choose lost item support',
        'Describe the missing item',
        'Wait for support follow-up',
      ],
      highlightTitle: 'Item recovery',
      highlightBody:
          'SafarPay can help coordinate recovery, but cannot guarantee that an item will be found.',
      relatedArticleIds: ['report-driver', 'cancel-ride'],
    ),
  ];

  static SFaqArticle articleById(String id) {
    return popularArticles.firstWhere((article) => article.id == id);
  }

  static List<SFaqArticle> articlesForCategory(String categoryId) {
    return popularArticles
        .where((article) => article.categoryId == categoryId)
        .toList(growable: false);
  }
}
