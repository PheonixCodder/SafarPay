# Auth User Cache Plan

## Goal

Cache the authenticated `/me` user locally for non-authoritative UI display and remove static demo profile values from Settings/Profile.

## Implementation

1. Extend `SUserResponse`.
   - Add `toJson()`.
   - Add `copyWith()` for local profile cache edits.

2. Add user cache storage.
   - Add `SUserStorage` under `utils/local_storage`.
   - Store one `current_user` JSON map through `SLocalStorage`.
   - Expose save, read, existence, and clear methods.

3. Add current user controller.
   - Add `SCurrentUserController`.
   - Load cached user on init.
   - Refresh from backend `/me`, save to cache, and update observable state.
   - Support local cache edits for name, email, phone, and profile image.

4. Wire auth lifecycle.
   - Auth gate refreshes `/me` into cache.
   - Register, Google login, and Google phone-link save tokens then refresh/cache `/me`.
   - Invalid session and logout clear both token storage and user cache.

5. Replace static user UI.
   - Settings profile tile reads cached name/email/image.
   - Profile screen initializes name/email/phone/image from cached user.
   - Gender and date of birth show `Not set`.
   - Local edits update the cached user until backend profile mutation APIs exist.

6. Update context.
   - Architecture, project overview, UI context, progress tracker, and decisions log.

## Verification

- `flutter test test/authentication/user_cache_test.dart --no-pub`
- Focused analyzer for auth storage/controller and Settings/Profile consumers.
- Attempt `dart format` on touched files; report timeout if it persists.
