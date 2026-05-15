# Prompt: Home Categories Widget

Create a light-mode categories widget for the home screen inside `client/lib/features/home/screens/widgets/categories.dart`.

## Prompt

Build a professional SafarPay home categories section that matches the attached reference layout in light mode. The widget should show Groceries, City rides, City to City, Couriers, and Freight using text from `STexts` and images from `SImages` under their Categories sections.

## Target Files

- `lib/features/home/screens/widgets/categories.dart`
- `lib/features/home/screens/home/home.dart`
- `lib/utils/constants/texts.dart`
- `lib/utils/constants/images.dart`
- `pubspec.yaml`
- `client/context/**`
- `client/plans/**`

## Acceptance Criteria

- Public widget is named `SHomeCategories`.
- Categories use `STexts` for every visible label.
- Category images use `SImages` and point to `assets/images/categories/`.
- `pubspec.yaml` declares `assets/images/categories/`.
- UI uses `SColors` and `SSizes`; no raw `Colors.*` in `categories.dart`.
- Layout mirrors the reference: dominant Groceries tile, stacked City rides and City to City tiles, then Couriers and Freight tiles below.
- Groceries includes an ETA subtitle and `NEW` badge.
- The widget is wired into the home screen below the carousel.
- Context docs, plans, and decisions log are updated.
