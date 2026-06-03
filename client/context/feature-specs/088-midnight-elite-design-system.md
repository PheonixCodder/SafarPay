# Midnight Elite Design System (088)

## Prompt

Migrate the entire SafarPay Flutter client (`client/`) to the **Midnight Elite** design system defined in [DESIGN.md](../DESIGN.md). Replace the legacy light/teal + SF Pro stack with a single dark theme, Plus Jakarta Sans + Inter typography, gold primary actions, and charcoal surfaces.

**Do not change:** business logic, API contracts, navigation flows, GetX controller behavior, or backend integration.

## Requirements

### Typography

- Register **Plus Jakarta Sans** (display/headline/title) and **Inter** (body/labels) in `pubspec.yaml`.
- Implement scale in `lib/utils/constants/typography.dart` (`STypography`).
- Map Material `TextTheme` via `STextTheme` / `STypography.toTextTheme()`.
- Remove all `SF-Pro` references.

### Colors

- Implement Material 3 roles from DESIGN.md frontmatter in `SColors`.
- Semantic tokens: `gold`, `pickup` (green), `destination` (red), `inputFill`, `cardElevated`.
- Legacy aliases (`textPrimary`, `primaryBackground`, `light`, etc.) point to dark tokens for gradual migration.
- No new raw hex in feature widgets.

### Theme

- `SAppTheme.appTheme` with `Brightness.dark` only.
- Pill primary buttons (gold fill, dark text).
- 32px top corner radius on bottom sheets.
- 20px card radius; charcoal card surfaces.
- `app.dart`: `ThemeMode.dark`, Shad dark scheme.

### Components (DESIGN.md)

- **Buttons:** Gold primary, outlined secondary (white 20% stroke).
- **Inputs:** Pill-shaped, `#16181C` fill, gold focus border.
- **Chips:** 40px pill; selected = gold.
- **Map:** Green pickup marker, red destination, gold route line.
- **Navigation:** Floating bar with gold active indicator/glow.

### Settings

- Hide or remove non-functional **Dark Mode** row (app is dark-only).

## Key files

| Area | Path |
|------|------|
| Design source | `context/DESIGN.md` |
| Colors | `lib/utils/constants/colors.dart` |
| Typography | `lib/utils/constants/typography.dart` |
| Sizes | `lib/utils/constants/sizes.dart` |
| Theme | `lib/utils/theme/theme.dart`, `custom_themes/*` |
| App entry | `lib/app.dart` |

## Acceptance criteria

- [ ] App runs with dark charcoal UI and gold CTAs on all main flows.
- [ ] No `SF-Pro`, `0xFF338B95`, or `Brightness.light` in theme layer.
- [ ] `flutter analyze` passes on `client/`.
- [ ] `ui-context.md` documents Midnight Elite tokens.
- [ ] Map pickup/destination markers match DESIGN colors.

## Test plan

1. `cd client && flutter pub get`
2. `flutter analyze --no-pub`
3. `flutter test`
4. Manual: onboarding → login → OTP → home → ride search → trips → settings → driver mode
