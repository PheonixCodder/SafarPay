# SafarPay Client Project Overview

## Overview

SafarPay is a ride-hailing mobile client for riders who need a fast, trustworthy way to start a trip, verify their identity, and move into the main app experience. The current client has the Flutter scaffold, shared design foundation, onboarding, phone OTP authentication, Google authentication with phone linking, profile completion, permissions, a four-tab post-auth navigation shell, passenger map-first booking foundations, and the starter driver registration entry flow in place.

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
8. User reaches `NavigationMenu`, where `HomeScreen` is the first tab.

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
- Post-auth routing to `NavigationMenu` when permissions are complete.
- Personalization settings starter screen with account, app setting rows, profile entry, and logout action.
- Personalization profile screen is reachable from Settings through the profile edit action and `User Info` row.
- Personalization profile values can be edited locally through a reusable common edit drawer.

### Navigation

- Four-tab shell with Home, Trips, Rent, and Profile destinations.
- Home remains the first tab, Trips and Rent are starter states, and Profile opens the Settings experience.

### Ride Data And Search

- Typed demo ride responses mirror the backend ride contract.
- Home shows two recent demo ride destinations below the search bar.
- Home includes a local banner carousel for ride and promotion imagery.
- Home includes static service category entry points for Groceries, City rides, City to City, Couriers, and Freight.
- Home search opens the passenger map-first booking flow with pickup detection, backend geocode search, map-pin location selection, route preview, category/vehicle selection, hybrid offer creation, live bid updates, passenger counter-offers, and bid acceptance plumbing.
- Home service category tiles open the same booking flow with the tapped service category preselected.
- Passenger map-first booking currently uses temporary local demo responses and demo socket streams while services are down. Real Location, Geospatial, Ride, Bidding HTTP routes, and Ride/Bidding WebSocket blocks remain commented in code for restoration.

### Driver Registration

- Settings opens a driver registration flow from `Register as a Driver`.
- Users choose an earning category, choose a vehicle option for that category, and then see a Verification-service-backed checklist.
- The checklist reads `GET /api/v1/verification/me` and renders CNIC, license, selfie, and vehicle status groups.
- CNIC, license, selfie-with-license, and vehicle info pages collect their own data, request presigned upload URLs from the Verification service, and upload documents directly to those URLs.

### Client Foundation

- Centralized theme, colors, sizes, strings, validators, helpers, HTTP client, and local storage utilities.
- Native Mapbox map rendering, foreground GPS, backend geospatial repositories, Ride/Bidding repositories, and separate Location/Ride/Bidding WebSocket primitives.
- Feature-first structure under `lib/features`.
- Context, feature-spec, plan, and decision documentation under `client/context` and `client/plans`.
- Help & Support includes a local Terms & Conditions legal hub with typed static policy content and expandable detail pages.
- Help & Support includes local FAQ categories, search, popular articles, article detail pages, related links, and helpful controls.

## Scope

### In Scope

- Flutter mobile client structure and UI.
- Authentication screens and state flow.
- Local token and preference storage.
- Firebase/Google setup files needed for client auth.
- Shared UI constants and app theme.
- Typed demo data for frontend UI development plus real backend route/socket paths for Ride and Bidding integration.
- Local home banner carousel assets.
- Local home category assets and static category UI.
- Personalization settings UI cleanup and reusable settings components.
- Help & Support informational policy pages with local static Terms & Conditions content.
- Help & Support FAQ categories, popular articles, and article details backed by local static content.
- Reusable page transition helpers for common non-auth navigation patterns.
- Reusable shadcn edit drawer for existing-value edits.
- Driver registration entry, vehicle selection, Verification `/me` status rendering, KYC step submissions, and presigned document upload UI.

### Out Of Scope

- Backend service implementation.
- Payment backend implementation.
- Dedicated full-screen live bidding display, payment settlement, rental, profile management, and wallet UI beyond starter placeholders.
- Production analytics, crash reporting, and release automation until explicitly planned.
- Real auth API integration is out of scope for the current completed UI/mock phase.

## Success Criteria

1. A new user can complete phone OTP registration and reach permissions or home.
2. A Google user with `phoneRequired == true` is routed to a dedicated phone-link screen instead of staying on login.
3. A Google user with `phoneRequired == false` reaches permissions or home.
4. UI remains consistent with SafarPay color, typography, spacing, and auth layout rules.
5. Future agents can understand product state by reading `client/context` and `client/plans`.
