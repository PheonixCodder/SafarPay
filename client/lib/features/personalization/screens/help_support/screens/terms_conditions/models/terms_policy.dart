import 'package:flutter/widgets.dart';

class STermsPolicy {
  const STermsPolicy({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.lastUpdated,
    required this.sections,
  });

  final String id;
  final String title;
  final String subtitle;
  final IconData icon;
  final String lastUpdated;
  final List<STermsPolicySection> sections;
}

class STermsPolicySection {
  const STermsPolicySection({
    required this.title,
    required this.body,
  });

  final String title;
  final String body;
}
