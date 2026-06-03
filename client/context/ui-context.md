# UI Context

## Theme

SafarPay uses the **Midnight Elite** dark design system ([DESIGN.md](./DESIGN.md)): true-black/charcoal surfaces, gold primary actions, high-contrast typography, and glass-friendly navigation. The app runs **dark mode only** (no light theme in this release).

## Colors

All app colors come from `SColors` in `lib/utils/constants/colors.dart`.
Reusable alpha values come from `SOpacities`, applied through `SHelperFunctions.withOpacity`.

| Role | Token | Value |
| --- | --- | --- |
| Page background | `SColors.background` | `#121414` |
| Card / sheet surface | `SColors.surfaceContainer` | `#1E2020` |
| Elevated modal | `SColors.cardElevated` | `#1B1D22` |
| Input fill | `SColors.inputFill` | `#16181C` |
| Primary accent (gold) | `SColors.primaryContainer` / `SColors.gold` | `#F6C21A` |
| Primary text on gold | `SColors.onPrimary` | `#3E2E00` |
| Body text | `SColors.onSurface` | `#E3E2E2` |
| Muted text | `SColors.onSurfaceVariant` | `#D2C5AC` |
| Outline | `SColors.outline` | `#9B9079` |
| Pickup marker | `SColors.pickup` | Green |
| Destination marker | `SColors.destination` | Red |
| Error | `SColors.error` | `#FFB4AB` |

Do not hard-code new hex values in feature UI unless the color is first added to `SColors`.

Legacy aliases (`textPrimary`, `primary`, `light`, `primaryBackground`) remain for migration but map to Midnight Elite tokens.

## Typography

| Role | Font | Source |
| --- | --- | --- |
| Display / headline / title | Plus Jakarta Sans | `pubspec.yaml` → `PlusJakartaSans` |
| Body / labels | Inter | `pubspec.yaml` → `Inter` |
| Scale | `STypography` | `lib/utils/constants/typography.dart` |
| Material mapping | `STextTheme.appTextTheme` | `lib/utils/theme/custom_themes/text_theme.dart` |

Use theme text styles; override weight, color, or alignment only when needed. No italic faces.

## Spacing And Radius

Use `SSizes` for spacing, icon sizes, card radius, field spacing, and loading indicator dimensions.

| Context | Token examples |
| --- | --- |
| Base grid | `SSizes.unit` (8px) |
| Screen padding | `SSizes.screenPadding` (24) |
| Small gaps | `SSizes.xs`, `SSizes.sm` |
| Pill buttons / chips | `SSizes.radiusPill`, `SSizes.chipHeight` |
| Cards | `SSizes.cardRadiusLg` (20) |
| Bottom sheets | `SSizes.sheetRadiusXl` (32) |

## Component Conventions

- Scaffolds use `SColors.background`.
- Cards and sheets use `SColors.surfaceContainer` (not pure white fills).
- Primary actions: gold pill `ElevatedButton` (`SColors.primaryContainer` + `SColors.onPrimary` text).
- Secondary actions: outlined pill (white stroke @ 20% opacity).
- Search fields: pill shape, `SColors.inputFill`, gold focus border.
- Use `TextFormField` with validators from `SValidator`.
- Keep `Obx` scoped to the smallest changing widget.

## Icons

Use `iconsax` icons. Sizes: `SSizes.iconSm`, `SSizes.iconMd`, `SSizes.iconLg`. Default icon color: `SColors.onSurface`.

## Layout Patterns And Completed Screens

- Onboarding: full-screen paged layout with bottom navigation controls on dark background.
- Login: dark minimalist form, gold pill Continue, Pakistan phone row.
- OTP: header, custom OTP input, verify/resend actions.
- Navigation menu: charcoal bottom bar, gold active tab indicator with subtle glow.
- Passenger booking: map-first with 32px top sheet radius, green/red markers, gold route.
- Settings: charcoal header, surface cards; Dark Mode row removed/disabled (dark-only app).
- Help & Support: charcoal header (no teal), support illustration, dark options sheet.

## Current Visual Assets

- Logo: `assets/logos/logo.png`.
- Fonts: `assets/fonts/PlusJakartaSans-Variable.ttf`, `Inter-Variable.ttf`.
- See [DESIGN.md](./DESIGN.md) for full shape, elevation, and glass rules.
