# Midnight Elite Design System Plan (088)

## Summary

Rebrand the SafarPay Flutter client to the **Midnight Elite** dark design system ([DESIGN.md](../context/DESIGN.md)): Plus Jakarta Sans + Inter, Material 3 dark `ColorScheme`, gold accents, pill CTAs, and charcoal surfaces.

**Scope:** Single dark theme only (no light theme, no Settings dark-mode toggle).

## Phases

### Phase 0 — Fonts (done)

- [x] Add `PlusJakartaSans-Variable.ttf` and `Inter-Variable.ttf` under `assets/fonts/`
- [x] Update `pubspec.yaml` font families; remove SF Pro

### Phase 1 — Tokens (done)

- [x] Rewrite `lib/utils/constants/colors.dart` (M3 roles + semantic pickup/destination/gold)
- [x] Add `lib/utils/constants/typography.dart` (`STypography`)
- [x] Extend `lib/utils/constants/sizes.dart` (8px grid, pill radius, 32px sheets)

### Phase 2 — Theme (done)

- [x] `SAppTheme.appTheme` (dark `ColorScheme`)
- [x] Update all `custom_themes/*` + add `card_theme`, `divider_theme`, `navigation_bar_theme`
- [x] `app.dart`: `ThemeMode.dark`, Shad dark scheme

### Phase 3 — Context (done)

- [x] Update `context/ui-context.md`, `context/code-standards.md`, `plans/decisions-log.md`
- [x] Add `context/feature-specs/088-midnight-elite-design-system.md`

### Phase 4 — Widget migration (done)

- [x] Bulk card backgrounds: `SColors.white` → `SColors.surfaceContainer`
- [x] Map markers: pickup green, destination red, route gold
- [x] Navigation bar + tabs: gold active state
- [x] Primary header: charcoal surface
- [x] Login CTA: gold pill button

### Phase 5 — Verification

- [x] `dart format` on touched Dart files
- [x] `flutter analyze --no-pub` (warnings only, no errors)
- [x] `flutter test` (154+ passed; 2 driver tests have async teardown flakes)
- [ ] Visual smoke: auth → home → ride search → settings

## PR split (optional)

1. Tokens + theme + fonts + context
2. Common + auth widgets
3. Home + location + map
4. Trips + driver + communication + personalization

## Out of scope

- Light theme / dark-mode toggle
- Custom Mapbox style URL
- Marketing asset redraws
