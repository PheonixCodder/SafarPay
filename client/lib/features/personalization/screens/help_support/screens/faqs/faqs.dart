import 'package:flutter/material.dart';

import '../../../../../../common/navigation/right_slide_page_route.dart';
import '../../../../../../common/widgets/appbar/appbar.dart';
import '../../../../../../utils/constants/colors.dart';
import '../../../../../../utils/constants/sizes.dart';
import '../../../../../../utils/constants/texts.dart';
import 'data/faqs_data.dart';
import 'models/faq_models.dart';
import 'screens/faq_article_detail.dart';
import 'widgets/faq_category_card.dart';
import 'widgets/faq_popular_articles_card.dart';
import 'widgets/faq_search_field.dart';

class FaqsScreen extends StatefulWidget {
  const FaqsScreen({super.key});

  @override
  State<FaqsScreen> createState() => _FaqsScreenState();
}

class _FaqsScreenState extends State<FaqsScreen> {
  String _query = '';
  SFaqCategory? _selectedCategory;

  bool get _isSearching => _query.trim().isNotEmpty;

  List<SFaqCategory> get _filteredCategories {
    if (!_isSearching) return SFaqsData.categories;

    final normalizedQuery = _query.trim().toLowerCase();
    return SFaqsData.categories.where((category) {
      return category.title.toLowerCase().contains(normalizedQuery) ||
          category.subtitle.toLowerCase().contains(normalizedQuery);
    }).toList(growable: false);
  }

  List<SFaqArticle> get _visibleArticles {
    if (_isSearching) {
      final normalizedQuery = _query.trim().toLowerCase();
      return SFaqsData.popularArticles.where((article) {
        final bulletText = article.bullets.join(' ').toLowerCase();
        return article.title.toLowerCase().contains(normalizedQuery) ||
            article.summary.toLowerCase().contains(normalizedQuery) ||
            article.sectionTitle.toLowerCase().contains(normalizedQuery) ||
            bulletText.contains(normalizedQuery);
      }).toList(growable: false);
    }

    final selectedCategory = _selectedCategory;
    if (selectedCategory != null) {
      return SFaqsData.articlesForCategory(selectedCategory.id);
    }

    return SFaqsData.popularArticles;
  }

  String get _articleSectionTitle {
    if (_isSearching) return 'Search Results';
    final selectedCategory = _selectedCategory;
    if (selectedCategory != null) return '${selectedCategory.title} Articles';
    return 'Popular Articles';
  }

  void _onSearchChanged(String value) {
    setState(() {
      _query = value;
      if (value.trim().isNotEmpty) _selectedCategory = null;
    });
  }

  void _onCategorySelected(SFaqCategory category) {
    setState(() {
      _selectedCategory = category;
      _query = '';
    });
  }

  void _openArticle(BuildContext context, SFaqArticle article) {
    Navigator.of(context).push(
      SRightSlidePageRoute(
        page: FaqArticleDetailScreen(article: article),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final categories = _filteredCategories;
    final articles = _visibleArticles;

    return Scaffold(
      backgroundColor: SColors.primaryBackground,
      appBar: const SAppBar(
        showBackArrow: true,
        title: Text(STexts.helpSupportFaqs),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          physics: const BouncingScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(
            SSizes.defaultSpace,
            SSizes.md,
            SSizes.defaultSpace,
            SSizes.xl,
          ),
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  SFaqSearchField(onChanged: _onSearchChanged),
                  const SizedBox(height: SSizes.lg),
                  Text(
                    'Categories',
                    style: textTheme.labelLarge?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: SSizes.sm),
                  SFaqCategoryCard(
                    categories: categories,
                    onCategorySelected: _onCategorySelected,
                  ),
                  const SizedBox(height: SSizes.lg),
                  Text(
                    _articleSectionTitle,
                    style: textTheme.labelLarge?.copyWith(
                      color: SColors.textPrimary,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                  const SizedBox(height: SSizes.sm),
                  if (articles.isEmpty)
                    _FaqEmptyState(
                      message: _isSearching
                          ? 'No articles found for "$_query".'
                          : 'No articles available for this category.',
                    )
                  else
                    SFaqPopularArticlesCard(
                      articles: articles,
                      onArticleSelected: (article) =>
                          _openArticle(context, article),
                    ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _FaqEmptyState extends StatelessWidget {
  const _FaqEmptyState({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(SSizes.lg),
      decoration: BoxDecoration(
        color: SColors.white,
        borderRadius: BorderRadius.circular(SSizes.cardRadiusLg),
        border: Border.all(color: SColors.borderSecondary),
      ),
      child: Text(
        message,
        textAlign: TextAlign.center,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: SColors.textSecondary,
              fontWeight: FontWeight.w600,
            ),
      ),
    );
  }
}
