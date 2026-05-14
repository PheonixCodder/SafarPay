# Client Product And Architecture Plan

## Summary

Build SafarPay as a Flutter ride-hailing client with a feature-first architecture, a centralized design foundation, onboarding, auth, permissions, and a starter home screen. Current scope is rider-oriented client foundation and auth UI/mock flows.

## Key Changes

- Use Flutter, Dart, GetX, GetStorage, secure token storage, Firebase Core, and Google Sign-In.
- Keep app root in `main.dart` and `app.dart`, with `AuthGateScreen` as the first screen.
- Organize product code under `lib/features`, shared UI under `lib/common`, and app utilities under `lib/utils`.
- Centralize auth calls in `SAuthRepository` and secure token persistence in `STokenStorage`.

## Test Plan

- App launches to auth gate.
- Token state routes correctly.
- Context files describe all completed features and known gaps.

## Status

- Implemented for current client foundation and auth UI/mock scope.
