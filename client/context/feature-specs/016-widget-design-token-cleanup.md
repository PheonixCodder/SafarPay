# Prompt: Widget Design Token Cleanup

Refactor the updated notification, home categories, and ride search result widgets so their upgraded designs keep the same visual output while moving hard-coded spacing, sizing, opacity, and label values into `client/lib/utils`.

## Prompt

The widgets `client/lib/common/widgets/notification.dart`, `client/lib/features/home/screens/widgets/categories.dart`, and `client/lib/common/widgets/ride/search_result.dart` received a design upgrade but now contain static values and local styling decisions. Preserve the current design exactly, but move reusable dimensions, opacity values, colors, text, and helper behavior into the existing SafarPay utility system.

## Target Files

- `lib/common/widgets/notification.dart`
- `lib/features/home/screens/widgets/categories.dart`
- `lib/common/widgets/ride/search_result.dart`
- `lib/utils/constants/colors.dart`
- `lib/utils/constants/sizes.dart`
- `lib/utils/constants/texts.dart`
- `lib/utils/helpers/helpers.dart`
- `client/context/**`
- `client/plans/**`

## Acceptance Criteria

- Current visual design is not intentionally changed.
- Touched widgets use `SColors`, `SOpacities`, `SSizes`, `STexts`, and `SHelperFunctions`.
- Touched widgets do not use raw `Colors.*`.
- Touched widgets do not keep local opacity literals or local hard-coded display text.
- Notification count is configurable while keeping the current default.
- Notification widget follows the `S` class prefix convention while preserving the old name as a compatibility alias.
- Shared opacity application lives in `client/lib/utils/helpers`.
- Context docs, plans, and decisions are updated where relevant.
