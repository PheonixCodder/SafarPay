# SafarPay Client Project Overview

## Overview

SafarPay is a ride-hailing mobile client for riders who need a fast, trustworthy way to start a trip, verify their identity, and move into the main app experience. The current client has the Flutter scaffold, shared design foundation, onboarding, phone OTP authentication, Google authentication with phone linking, profile completion, permissions, and a starter home screen in place.

## Goals

1. Let a rider enter the app through phone OTP or Google without confusing account-state transitions.
2. Keep onboarding, authentication, and permissions simple enough to complete on a mobile device in one session.
3. Match the SafarPay backend auth model: phone-first registration, Google verification, optional Google phone linking, token storage, and post-auth permission gating.
4. Maintain a consistent mobile UI language across onboarding, login, OTP, profile, permissions, and home.

## Core User Flow

1. User opens the app and lands in `AuthGateScreen`.
2. If unauthenticated, the user enters `AuthFlowScreen`.
3. User completes or skips onboarding and reaches `LoginScreen`.
4. User chooses phone OTP or Google.
5. Phone OTP flow sends a code, verifies it, and completes profile registration.
6. Google flow verifies Google identity and either proceeds directly or asks for phone linking.
7. Authenticated users complete location and notification permissions.
8. User reaches `HomeScreen`.

## Features

### Onboarding

- Three-page onboarding with ride-hailing value props.
- Smooth page transitions and skip/get-started actions.

### Authentication

- Phone OTP send and verify flow.
- Google Sign-In flow.
- Dedicated Google phone-link screen when a Google account needs a phone number.
- Token storage with `flutter_secure_storage`.
- Mock repository implementations for auth endpoints until backend wiring is finalized.

### Profile And Permissions

- Profile completion after phone OTP registration.
- Location and notification permission flow.
- Post-auth routing to home when permissions are complete.

### Client Foundation

- Centralized theme, colors, sizes, strings, validators, helpers, HTTP client, and local storage utilities.
- Feature-first structure under `lib/features`.
- Context, feature-spec, plan, and decision documentation under `client/context` and `client/plans`.

## Scope

### In Scope

- Flutter mobile client structure and UI.
- Authentication screens and state flow.
- Local token and preference storage.
- Firebase/Google setup files needed for client auth.
- Shared UI constants and app theme.

### Out Of Scope

- Backend service implementation.
- Payment backend implementation.
- Full ride booking, bidding, live tracking, and wallet UI beyond starter placeholders.
- Production analytics, crash reporting, and release automation until explicitly planned.
- Real auth API integration is out of scope for the current completed UI/mock phase.

## Success Criteria

1. A new user can complete phone OTP registration and reach permissions or home.
2. A Google user with `phoneRequired == true` is routed to a dedicated phone-link screen instead of staying on login.
3. A Google user with `phoneRequired == false` reaches permissions or home.
4. UI remains consistent with SafarPay color, typography, spacing, and auth layout rules.
5. Future agents can understand product state by reading `client/context` and `client/plans`.
