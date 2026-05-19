import 'package:flutter/widgets.dart';

class SFaqCategory {
  const SFaqCategory({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.icon,
  });

  final String id;
  final String title;
  final String subtitle;
  final IconData icon;
}

class SFaqArticle {
  const SFaqArticle({
    required this.id,
    required this.categoryId,
    required this.title,
    required this.summary,
    required this.sectionTitle,
    required this.bullets,
    required this.highlightTitle,
    required this.highlightBody,
    required this.relatedArticleIds,
  });

  final String id;
  final String categoryId;
  final String title;
  final String summary;
  final String sectionTitle;
  final List<String> bullets;
  final String highlightTitle;
  final String highlightBody;
  final List<String> relatedArticleIds;
}
