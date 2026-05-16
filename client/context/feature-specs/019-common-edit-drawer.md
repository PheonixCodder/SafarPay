# Prompt: Common Edit Drawer

Create a reusable SafarPay edit drawer for updating existing profile/settings values with `shadcn_ui`.

## Goal

Add a common right-side drawer that can edit an existing value, then use it from the personalization profile screen rows.

## Requirements

- Add `shadcn_ui: ^0.54.0` to the Flutter client.
- Configure the app so shadcn widgets can be used alongside the existing GetX/Material app setup.
- Use the local skill docs at `client/.agents/skills/shadcn-ui-flutter/SKILL.md` whenever shadcn widgets are introduced or changed.
- Create a reusable common drawer under `client/lib/common/widgets/drawers`.
- The drawer must accept the value being edited, field label, title, description, keyboard type, optional validator, and save callback.
- Use `showShadSheet` with `ShadSheetSide.right`, `ShadSheet`, `ShadInput`, and `ShadButton`.
- Keep the visual language aligned with `SColors`, `SSizes`, `SOpacities`, and SafarPay typography.
- Change `SProfileMenu` to show a boxed edit icon instead of a right-arrow icon.
- Opening a profile menu row should show the common drawer with that row's current value and data type.
- Saving should update the visible profile value locally for the current session.
- Do not add backend persistence in this unit.

## Acceptance Criteria

1. The app can render shadcn sheet components inside the existing GetX app.
2. Profile rows show a boxed edit icon.
3. Tapping Name, E-mail, Phone Number, Gender, or Date of Birth opens the common edit drawer.
4. The drawer starts with the row's current value.
5. Saving updates the value displayed on the profile screen.
6. Dismissing without saving leaves the value unchanged.
7. The common drawer remains reusable by future settings subpages.
