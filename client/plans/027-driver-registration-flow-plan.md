# Driver Registration Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the Settings-driven driver registration entry flow with category selection, vehicle selection, Verification `/me` status rendering, and four skeleton checklist step screens.

**Architecture:** Keep the feature under `features/personalization/screens/driver_registration`, with typed models, a Verification repository, a GetX controller, and focused reusable widgets. The backend remains the source of truth for registration state through `GET /api/v1/verification/me`.

**Tech Stack:** Flutter, Dart, GetX, existing `SHttpClient`, `SRightSlidePageRoute`, `SPrimaryHeaderContainer`, `SColors`, `SSizes`, `STexts`, `SImages`, and Iconsax.

---

## Tasks

- [ ] Add Verification service configuration by extending `SApiService` and `SApiConstants.verificationBaseUrl`.
- [ ] Add driver registration image constants and asset directories in `SImages` and `pubspec.yaml`.
- [ ] Add driver registration text constants to `STexts`.
- [ ] Create typed driver registration models for categories, vehicle options, backend status parsing, grouped requirement statuses, and checklist steps.
- [ ] Create `SDriverVerificationRepository.getMyVerificationStatus()` using `SHttpClient.get('/me', service: SApiService.verification, requiresAuth: true)`.
- [ ] Create `SDriverVerificationController` to load status, expose loading/error state, and map backend group statuses to checklist card view data.
- [ ] Create reusable light-mode option and verification-step card widgets.
- [ ] Implement `DriverRegistrationScreen` for the five earning categories.
- [ ] Implement `DriverVehicleSelectionScreen` for category-specific vehicles.
- [ ] Implement `DriverVerificationStatusScreen` with primary header, driver image, overall status notice, pull-to-refresh, loading/error states, and four checklist cards.
- [ ] Implement skeleton screens for CNIC Info, Driver's License, Selfie with License, and Vehicle Info.
- [ ] Wire the Settings `Register as a Driver` row to `DriverRegistrationScreen` through `SRightSlidePageRoute`.
- [ ] Add feature-spec and plan documents, then update architecture, UI context, progress tracker, and decisions log.
- [ ] Run `flutter analyze` and `flutter test` from `client/`.

## Acceptance Criteria

- Tapping Settings > Register as a Driver opens the category selection screen.
- Selecting a category opens the correct vehicle list.
- Selecting a vehicle opens the verification checklist status screen.
- The checklist calls `/api/v1/verification/me` through the Verification service base URL.
- Checklist cards reflect `not_started`, `pending`, `under_review`, `rejected`, and `verified` states.
- Under-review and verified states block checklist card navigation.
- Rejected groups show a cross icon and rejection reason when the backend provides one.
- Each checklist card routes to the correct skeleton screen when enabled.

## Deferred

- CNIC form fields and image upload.
- Driver license form fields and image upload.
- Selfie capture/upload.
- Vehicle info form and document upload.
- Direct S3 PUT uploads through presigned URLs.
- `POST /api/v1/verification/submit-review`.
- Backend vehicle enum reconciliation for UI options beyond `moto`, `economy`, `comfort`, and `freight`.
