# Auth Profile Demographics

## Prompt

Add email, gender, and date of birth to backend Auth profile persistence and the Flutter profile completion flow. The Complete Profile screen should collect email, gender, and DOB in addition to name, using the same date picker/date field pattern used in the driver CNIC screen.

Persist these fields in `auth.users`, return them from `/me`, show them in the Profile screen, and add an authenticated backend route for updating editable user info: name, email, gender, and DOB. Phone number must remain read-only and must not be editable from the Profile screen.

Follow the existing backend layering: router, schemas, dependency injection, use cases, domain models, repositories, ORM, and migration. Follow the existing client context and folder structure.

## Acceptance Criteria

- `POST /api/v1/auth/register` accepts and persists `email`, `gender`, and `date_of_birth`.
- `GET /api/v1/auth/me` returns `gender` and `date_of_birth`.
- `PATCH /api/v1/auth/me` updates only name, email, gender, and DOB.
- Phone is not accepted as an editable profile field.
- Gender values are `male`, `female`, and `other`.
- DOB is required during profile completion and must be at least 13 years old.
- Existing users with missing gender/DOB can still load and show `Not set`.
- Backend docs, client context, plan, and decision log are updated.
