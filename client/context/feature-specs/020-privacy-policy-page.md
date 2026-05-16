# Prompt: Privacy Policy Page

Create a professional Privacy Policy page for the SafarPay Flutter client and open it from Settings.

## Goal

When the rider taps `Privacy & Security` in `client/lib/features/personalization/screens/settings/settings.dart`, open a new privacy policy screen with the same right-slide transition used for the personalization profile page.

## Requirements

- Read `client/AGENTS.md` and the context files before editing.
- Add the page under `client/lib/features/personalization/screens/privacy_policy`.
- Keep policy content in a separate mapped content file, not hard-coded repeatedly in the widget tree.
- Add screen-local widgets under `privacy_policy/widgets`.
- Follow the one-primary-widget-per-file pattern.
- Use `SAppBar`, `SRightSlidePageRoute`, `SColors`, `SSizes`, `SOpacities`, `SHelperFunctions`, `STexts`, and Iconsax.
- Match the existing Settings/Profile personalization visual language.
- Make the page interactive with expandable policy sections.
- Add polished placeholder policy content that can be replaced later.
- Do not add backend calls, persisted consent, or legal acceptance state in this unit.
- Keep `User Info` navigation to `ProfileScreen` unchanged.
- Update context docs, the saved implementation plan, progress, and decision log.

## Acceptance Criteria

1. Tapping `Privacy & Security` opens `PrivacyPolicyScreen`.
2. The page enters with `SRightSlidePageRoute` and back navigation returns to Settings.
3. Policy content is rendered from typed mapped section data.
4. Each policy section expands and collapses without layout overflow.
5. The page uses SafarPay colors, spacing, app bar, typography, and common navigation patterns.
6. Other Settings rows do not accidentally navigate.
