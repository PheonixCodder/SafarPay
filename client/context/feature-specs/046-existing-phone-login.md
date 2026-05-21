# Existing Phone Login Branch

## Prompt

When a user signs in with a phone number that already belongs to an existing account, the app should not send them to Complete Profile again. Keep the same Login and OTP screens, but after OTP verification the backend must detect whether the phone already has a user row.

If the phone already has an account, `/otp/verify` should issue the normal auth tokens and the Flutter client should route through the normal post-auth destination. If the phone is new, `/otp/verify` should return a registration/profile-completion token and the client should open Complete Profile. Google phone linking must keep working through the OTP screen without treating an existing phone as a direct phone login.

Follow the existing service boundaries, client folder structure, context workflow, and Auth service documentation pattern. Do not add out-of-place backend routes or client mocks.

## Acceptance Criteria

- Existing phone users verify OTP and enter the app without seeing Complete Profile.
- New phone users verify OTP and continue to Complete Profile.
- Google phone linking uses the OTP proof token and still calls the existing link-phone route.
- Backend request/response schemas make the next step explicit.
- Flutter parsing and routing are covered by focused tests.
- Auth service docs, client context, plan, AGENTS references, and decision log are updated.
