# Auth User Cache Prompt

Implement a lightweight authenticated user cache in the Flutter client.

## Source Request

After successful authentication, save the current user returned by `/me` in the client. Then go through the app and remove static user profile values so Settings/Profile use the saved user instead.

## Requirements

- The cached user is UI cache only; backend `/me` remains authoritative.
- Tokens remain in `STokenStorage`; user profile data must not be mixed with token storage.
- Add a dedicated user storage helper under `client/lib/utils/local_storage`.
- Serialize `SUserResponse` to and from JSON.
- Save the user after successful auth flows and after startup session validation.
- Clear cached user on logout or invalid session.
- Replace static Settings/Profile demo values with cached user fields.
- Keep unsupported profile fields, such as gender and date of birth, as explicit `Not set` fallbacks until backend support exists.
- Add focused tests for serialization, storage, Settings tile, and Profile screen rendering.
