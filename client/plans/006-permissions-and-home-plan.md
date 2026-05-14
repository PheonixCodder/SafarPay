# Permissions And Home Plan

## Summary

Build location and notification permission gating plus a starter home screen.

## Key Changes

- Add `SPermissionsController` with location-first then notification flow.
- Add reusable `SPermissionPage`.
- Persist completion flag in `SLocalStorage`.
- Route to `HomeScreen` after permissions.
- Add starter home with greeting and welcome content.

## Test Plan

- Permission flow starts with location.
- Accepted location advances to notification.
- Accepted notification completes permissions and goes home.
- Existing completion routes directly home.

## Status

- Implemented.
