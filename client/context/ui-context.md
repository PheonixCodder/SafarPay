# UI Context

## Theme

SafarPay uses a light, clean mobile design language for ride-hailing workflows. Authentication screens should feel secure, direct, and calm: light backgrounds, restrained teal accents, clear form hierarchy, generous touch targets, and simple progress through onboarding, login, OTP, profile, permissions, and home.

## Colors

All app colors should come from `SColors` in `lib/utils/constants/colors.dart`.

| Role | Token | Value |
| --- | --- | --- |
| Primary accent | `SColors.primary` | `0xFF338B95` |
| Secondary | `SColors.secondary` | `0xFF6B7280` |
| Accent | `SColors.accent` | `0xFFB0C7FF` |
| Page background | `SColors.primaryBackground` | `0xFFF9F9F9` |
| Surface | `SColors.white` | `Colors.white` |
| Light surface | `SColors.lightContainer` | `0xFFF6F6F6` |
| Primary text | `SColors.textPrimary` | `0xFF222222` |
| Secondary text | `SColors.textSecondary` | `0xFF6B7280` |
| Border | `SColors.borderSecondary` | `0xFFE6E6E6` |
| Error | `SColors.error` | `0xFFD32F2F` |
| Success | `SColors.success` | `0xFF388E3C` |

Do not hard-code new hex values in feature UI unless the color is first added to `SColors`.

## Typography

| Role | Font | Source |
| --- | --- | --- |
| App UI text | SF Pro | `pubspec.yaml` font family `SF-Pro` |
| Material text styles | `STextTheme.lightTextTheme` | `lib/utils/theme/custom_themes/text_theme.dart` |

Use theme text styles and override only weight, color, or alignment when needed.

## Spacing And Radius

Use `SSizes` for spacing, icon sizes, card radius, field spacing, and loading indicator dimensions.

| Context | Token examples |
| --- | --- |
| Small gaps | `SSizes.xs`, `SSizes.sm` |
| Form fields | `SSizes.spaceBtwInputFields` |
| Screen sections | `SSizes.spaceBtwSections`, `SSizes.defaultSpace` |
| Cards and panels | `SSizes.cardRadiusSm`, `SSizes.cardRadiusMd`, `SSizes.cardRadiusLg` |
| Buttons and fields | `SSizes.buttonRadius`, `SSizes.inputFieldRadius` |

## Component Conventions

- Authentication screens use `Scaffold`, `SafeArea`, `SingleChildScrollView`, centered `ConstrainedBox(maxWidth: 420)`, and `SColors.primaryBackground`.
- Use `TextFormField` with validators from `SValidator`.
- Use `ElevatedButton` for primary actions and `OutlinedButton` for secondary provider actions.
- Keep `Obx` scoped to the smallest changing widget.
- Use private widgets in the same screen file for one-off composition; move to `widgets/` when reused.

## Icons

Use `iconsax` icons for Flutter UI. Typical sizes come from `SSizes.iconSm`, `SSizes.iconMd`, and `SSizes.iconLg`.

## Layout Patterns And Completed Screens

- Onboarding: full-screen paged layout with bottom navigation controls.
- Login: header, phone form, divider, Google button.
- OTP: header, custom OTP input, verify/resend actions.
- Profile: header, form, terms agreement, primary continue action.
- Permissions: one focused permission request per page.
- Google phone link: identity confirmation card followed by phone number form; no Google button after Google verification.
- Home: centered starter state with app bar greeting and a large icon treatment.

## Current Visual Assets

- Logo: `assets/logos/logo.png`.
- Google icon: `assets/logos/google-icon.png`.
- Onboarding images: `assets/images/onboarding/ON1.jpg`, `ON2.jpg`, `ON3.jpg`.
- Icons: local SVG assets plus Iconsax for Flutter controls.
- Fonts: SF Pro Display variants declared in `pubspec.yaml`.
