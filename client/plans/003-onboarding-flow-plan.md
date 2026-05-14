# Onboarding Flow Plan

## Summary

Build a three-screen visual onboarding flow that introduces ride speed, safety, and honest pricing, then transitions to login.

## Key Changes

- Add `OnBoardingController` with page state, skip, next, and complete behavior.
- Add full-screen image onboarding pages with gradient overlays.
- Add dot indicator and bottom navigation buttons.
- Use `AuthFlowScreen` and `SAuthFlowController` for onboarding-to-login transition.

## Test Plan

- Next advances pages.
- Skip jumps to the final page.
- Get Started shows login.
- Onboarding images load and are precached.

## Status

- Implemented.
