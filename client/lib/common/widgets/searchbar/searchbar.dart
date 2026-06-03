import 'package:flutter/material.dart';

import '../../../utils/constants/colors.dart';
import '../../../utils/constants/sizes.dart';
import '../../../utils/device/utility.dart';

class SSearchBar extends StatelessWidget {
  const SSearchBar({
    super.key,
    required this.searchText,
    this.icon,
    this.endIcon,
    this.onPressed,
    this.showBackground = true,
    this.showBorder = true,
    this.padding = const EdgeInsets.symmetric(
      horizontal: SSizes.defaultSpace,
    ),
    this.contentPadding = const EdgeInsets.all(SSizes.md),
    this.width,
    this.backgroundColor,
    this.borderColor,
    this.borderRadius,
    this.textStyle,
    this.iconColor,
    this.endIconColor,
    this.iconSize,
    this.endIconSize,
    this.leading,
    this.trailing,
  });

  final String searchText;
  final IconData? icon;
  final IconData? endIcon;
  final VoidCallback? onPressed;
  final bool showBackground;
  final bool showBorder;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry contentPadding;
  final double? width;
  final Color? backgroundColor;
  final Color? borderColor;
  final BorderRadius? borderRadius;
  final TextStyle? textStyle;
  final Color? iconColor;
  final Color? endIconColor;
  final double? iconSize;
  final double? endIconSize;
  final Widget? leading;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    final effectiveIconColor = iconColor ?? SColors.onSurfaceVariant;
    final effectiveEndIconColor = endIconColor ?? SColors.onSurfaceVariant;

    return Padding(
      padding: padding,
      child: Material(
        color: SColors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: borderRadius ??
              BorderRadius.circular(
                SSizes.cardRadiusLg,
              ),
          child: Container(
            width: width ?? SDeviceUtils.getScreenWidth(context),
            padding: contentPadding,
            decoration: BoxDecoration(
              color: showBackground
                  ? backgroundColor ?? SColors.inputFill
                  : SColors.transparent,
              borderRadius: borderRadius ??
                  BorderRadius.circular(
                    SSizes.cardRadiusLg,
                  ),
              border: showBorder
                  ? Border.all(color: borderColor ?? SColors.outlineVariant)
                  : null,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Row(
                    children: [
                      if (leading != null)
                        leading!
                      else if (icon != null)
                        Icon(
                          icon,
                          color: effectiveIconColor,
                          size: iconSize,
                        ),
                      if (leading != null || icon != null)
                        const SizedBox(width: SSizes.spaceBtnItems),
                      Expanded(
                        child: Text(
                          searchText,
                          style: textStyle ??
                              Theme.of(context).textTheme.bodySmall,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                ),
                if (trailing != null)
                  trailing!
                else if (endIcon != null)
                  Icon(
                    endIcon,
                    color: effectiveEndIconColor,
                    size: endIconSize,
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
