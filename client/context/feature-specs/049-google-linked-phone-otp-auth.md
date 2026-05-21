# Google Linked Phone OTP Auth

## Prompt

When a passenger signs in with Google and the Google account is already linked to an Auth user, Auth must still check whether that linked user has a saved phone number.

If the linked user has a saved phone, do not issue access or refresh tokens immediately from `/google/verify-token`. Send an OTP to the saved phone, return `next_step=verify_existing_phone`, a masked phone, and a short-lived `google_login_token`. The frontend should reuse the existing OTP screen and only receive normal tokens from `/google/verify-existing-phone` after the OTP is verified.

If the linked Google user has no saved phone, keep the existing phone-link flow unchanged. If the Google account is not linked yet, keep the existing email-match and new-Google-user behavior unchanged.

Follow the existing Auth service pattern: router, schemas, use cases, dependency injection, repositories, and docs. Keep frontend behavior scoped to the already-supported `verify_existing_phone` response contract.
