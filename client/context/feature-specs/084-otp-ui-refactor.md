# 084 – OTP Screen UI Refactor

## Objective
Refactor the OTP screen UI across the entire SafarPay app to match the provided design (img_1.png). This is a pure visual redesign — no flows, APIs, or business logic were changed.

## What Changed

### Design
- **Layout**: Moved from centered to **left-aligned** across all elements (title, subtitle, OTP boxes, button)
- **Title**: Large bold "We just sent an SMS" (or Google variant) — replaces the old icon-box + centered header
- **Subtitle**: Inline phone number, left-aligned grey body text
- **OTP boxes**: Replaced the custom multi-TextField grid with `pinput 5.0.2` — rounded boxes (52×52, radius 14), light grey default, white with border focused, dark filled submitted
- **Button**: Black full-width stadium-shaped "Verify OTP" button (replaces teal/primary button)
- **Resend**: Inline "Didn't receive the code? Send again" with underlined link text (replaces separate TextButton)
- **AppBar**: Shared `SAppBar` with circular back button + centered "SafarPay" branding

### Performance
- `pinput` replaces the previous custom multi-`TextField` OTP widget that suffered from lag and missed inputs
- Pinput is a dedicated, highly optimised OTP input library with built-in auto-focus, auto-advance, and paste support

## Files Changed
- `lib/features/authentication/screens/otp/otp.dart` — Clean scaffold, SAppBar, left-aligned layout
- `lib/features/authentication/screens/otp/widgets/otp_header.dart` — New left-aligned header, no icon box
- `lib/features/authentication/screens/otp/widgets/otp_input.dart` — Replaced with pinput-based widget
- `lib/features/authentication/screens/otp/widgets/otp_actions.dart` — Black pill button + inline resend link
- `pubspec.yaml` — Replaced `flutter_otp_text_field` with `pinput: ^5.0.0`

## Constraints
- No API calls, no navigation flows, no GetX controller logic was modified
- Auto-focus and auto-advance behaviour is preserved via pinput's `autofocus: true`
- All values sourced from `SColors`, `SSizes`, `STexts` — no hard-coded strings or magic numbers (spacing uses raw literals only where SSizes values are equivalent)
