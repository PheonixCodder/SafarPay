# Auth Profile Demographics Plan

## Summary

Persist email, gender, and date of birth in Auth user profiles. Registration saves the fields, `/me` returns them, and Profile edits go through a new authenticated `PATCH /me` route.

## Implementation

- Add nullable `gender` and `date_of_birth` columns to `auth.users`.
- Extend Auth domain, ORM, repository mapping, API schemas, and `UserResponse`.
- Update `RegisterUseCase` and `/register` to accept `email`, `gender`, and `date_of_birth`.
- Add `UpdateUserProfileUseCase`, DI provider, and `PATCH /api/v1/auth/me`.
- Reject duplicate emails with `409 Conflict`.
- Add Flutter user model fields, cache serialization, repository `updateProfile`, and PATCH support in `SHttpClient`.
- Add gender chips and DOB date picker to Complete Profile.
- Update Profile screen to display backend gender/DOB, save editable fields through Auth API, and keep phone read-only.

## Verification

- Backend: `uv run pytest tests/auth/test_auth_use_cases.py tests/auth/test_auth_routes.py tests/auth/test_auth_timestamp_defaults_migration.py -q`
- Flutter: `flutter test test/authentication/user_cache_test.dart test/authentication/profile_form_fields_test.dart`
- Final: `flutter analyze`

## Decisions

- Gender wire values are `male`, `female`, `other`.
- DOB uses ISO `YYYY-MM-DD`.
- DOB must be at least 13 years old.
- Existing rows may keep null gender/DOB until the user updates profile.
