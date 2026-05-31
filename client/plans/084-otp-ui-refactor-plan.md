# 084 – OTP Screen UI Refactor Plan

## Scope
Pure UI redesign of the OTP screen to match `img_1.png`. No flows, APIs, controllers, or navigation logic changed.

## Files Modified

| File | Change |
|------|--------|
| `pubspec.yaml` | Replace `flutter_otp_text_field` → `pinput: ^5.0.0` |
| `screens/otp/otp.dart` | SAppBar + left-aligned Scaffold layout |
| `screens/otp/widgets/otp_header.dart` | Bold left-aligned title + subtitle, remove icon box |
| `screens/otp/widgets/otp_input.dart` | Pinput-based responsive OTP boxes |
| `screens/otp/widgets/otp_actions.dart` | Black pill verify button + inline resend link |

## Design Decisions

- **pinput** chosen for responsive, lag-free OTP input with built-in autofocus and paste support
- **PinTheme states**: default (grey box) → focused (white + dark border + shadow) → submitted (dark filled)  
- **Button**: `StadiumBorder` + `SColors.pureBlack` background — full width
- **Resend**: `RichText` inline "Didn't receive the code? Send again" with underline on action text
- All colours from `SColors`, spacing from `SSizes`, strings from `STexts`

## Status
✅ Complete — `flutter analyze` reports no issues
