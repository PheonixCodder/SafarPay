import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';

import '../../../../../../../utils/constants/colors.dart';
import '../../../../../../../utils/constants/sizes.dart';

class STermsDetailSectionTile extends StatefulWidget {
  const STermsDetailSectionTile({
    super.key,
    required this.index,
    required this.title,
    required this.body,
    this.initiallyExpanded = false,
  });

  final int index;
  final String title;
  final String body;
  final bool initiallyExpanded;

  @override
  State<STermsDetailSectionTile> createState() =>
      _STermsDetailSectionTileState();
}

class _STermsDetailSectionTileState extends State<STermsDetailSectionTile> {
  late bool _isExpanded;

  @override
  void initState() {
    super.initState();
    _isExpanded = widget.initiallyExpanded;
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final title = '${widget.index}. ${widget.title}';

    return DecoratedBox(
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(color: SColors.borderSecondary),
        ),
      ),
      child: Theme(
        data: Theme.of(context).copyWith(
          dividerColor: SColors.transparent,
          splashColor: SColors.transparent,
          highlightColor: SColors.transparent,
        ),
        child: ExpansionTile(
          initiallyExpanded: widget.initiallyExpanded,
          tilePadding: const EdgeInsets.symmetric(
            horizontal: SSizes.md,
            vertical: SSizes.xs,
          ),
          childrenPadding: const EdgeInsets.fromLTRB(
            SSizes.md,
            0,
            SSizes.md,
            SSizes.md,
          ),
          trailing: AnimatedRotation(
            turns: _isExpanded ? 0.5 : 0,
            duration: const Duration(milliseconds: 180),
            child: const Icon(
              Iconsax.arrow_down_1,
              size: SSizes.iconSm,
              color: SColors.textSecondary,
            ),
          ),
          onExpansionChanged: (value) {
            setState(() => _isExpanded = value);
          },
          title: Text(
            title,
            style: textTheme.labelLarge?.copyWith(
              color: SColors.textPrimary,
              fontWeight: FontWeight.w900,
            ),
          ),
          children: [
            Align(
              alignment: Alignment.centerLeft,
              child: Text(
                widget.body,
                style: textTheme.bodySmall?.copyWith(
                  color: SColors.textSecondary,
                  height: 1.45,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
