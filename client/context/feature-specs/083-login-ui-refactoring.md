# Login UI Refactoring (083)

## Prompt

Refactor the design of the SafarPay client login screen to match the clean visual style in the reference mockup, implementing a premium Pakistani country layout, custom back navigation, and cleaner form layout.

## Requirements

### 1. Custom App Bar Navigation
- Use `SAppBar` at the top of the login screen Scaffold.
- Modify the `SAppBar` widget inside [appbar.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/common/widgets/appbar/appbar.dart) to support a `showCircularBack` layout:
  - If `showCircularBack` is true, render a back arrow icon button wrapped in a circular container with `SColors.light` background color, invoking `leadingOnPressed` or popping the current route.
- Implement a smooth page transition between Onboarding and Login screens using [right_slide_page_route.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/common/navigation/right_slide_page_route.dart):
  - Completing onboarding pushes `LoginScreen` onto the navigation stack using `SRightSlidePageRoute`.
  - Tapping the login screen's app bar back button pops the login screen, performing the reverse transition smoothly.

### 2. Typographical improvements & Layout
- Remove the top background decorative container and stack from [login.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/authentication/screens/login/login.dart), converting it to a clean minimalist white-background layout.
- Include the brand logo side-by-side with the text "SafarPay" at the top of the form area in [header.dart](file:///C:/Users/ubaid/OneDrive/Desktop/SafarPay/client/lib/features/authentication/screens/login/widgets/header.dart).
- Align the header texts to the left for a modern mobile form feel:
  - Title: Large and bold "Welcome Back!" (size: 32).
  - Subtitle: Small, muted text "log in with your phone number" (size: 16, color: `SColors.textSecondary`).
- Label: Bold "Enter Your Phone number" placed directly above the input fields.

### 3. Phone Input Row Refactoring
- Wrap the inputs into a horizontal row container.
- **Left Side**: A clean, static container displaying the Pakistan flag (represented beautifully as `🇵🇰` or custom design) and `+92` country code prefix. It must not be a dropdown dropdown picker, only a static display.
- **Right Side**: Clean text field for typing the rest of the phone number.
- Standard phone validation and normalizer rules (`SPhoneNumberNormalizer.normalizeForPakistan`) must be kept intact.

### 4. CTA and Social Login Refactoring
- Render the primary button as a prominent dark pill-shaped "Continue" (or "Send OTP") button using `SColors.black` and stadium border style.
- Keep the social login buttons beneath the primary button.
- Remove the "Already have an account? Signin" section.
