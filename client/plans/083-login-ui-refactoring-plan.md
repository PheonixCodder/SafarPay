# Login UI Refactoring Plan (083)

## Plan

1. **Modify SAppBar (`appbar.dart`)**:
   - Add a `showCircularBack` boolean parameter (defaults to `false`).
   - If `showCircularBack` is true, display a centered `IconButton` wrapped in a circular decoration container with a light background (`SColors.light`).
   - Hook up `leadingOnPressed` to customize the pop transition.

2. **Update OnBoardingController (`onboarding.dart`)**:
   - In `completeOnboarding()`, transition to `LoginScreen` by pushing it with `SRightSlidePageRoute(page: const LoginScreen())` using the current BuildContext.

3. **Refactor SLoginHeader (`header.dart`)**:
   - Update `SLoginHeader` to render the logo icon next to the text "SafarPay" in a Row.
   - Left-align all texts.
   - Use bold "Welcome Back!" and subtitle "log in with your phone number" with responsive style/fonts.

4. **Refactor SLoginForm (`form.dart`)**:
   - Update form UI structure:
     - Add a text label "Enter Your Phone number" (bold, left-aligned).
     - Group the country code container and `TextFormField` side-by-side using a `Row`.
     - Static container for `🇵🇰 +92` prefix (matching typical height and rounded borders).
     - `TextFormField` without prefix icon, styled with rounded corners and clean borders.
     - Style the primary button to be dark pill-shaped using `SColors.black` and `StadiumBorder`.
     - Remove any potential "Already have an account?" text or section if present.

5. **Update LoginScreen (`login.dart`)**:
   - Use `SAppBar(showCircularBack: true, leadingOnPressed: () => SAuthFlowController.instance.showOnboarding())` as the `appBar` of the `Scaffold`.
   - Remove background positioned decorative containers.
   - Ensure child padding matches default margins.

6. **Verify with compiler / analyzer**:
   - Validate imports and verify that the page renders and behaves correctly.
