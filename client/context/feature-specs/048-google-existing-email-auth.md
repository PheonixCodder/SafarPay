# Google Existing Email Auth

## Prompt

When a passenger signs in with Google, Auth must check whether the verified Google email already belongs to an app user.

If the email belongs to an existing user with a phone number, do not create a duplicate Google user. Send an OTP to the saved phone, return only a masked phone plus a short-lived Google login token, and let the frontend verify that OTP before issuing normal auth tokens.

If the email belongs to an existing user without a phone number, link the Google account to that existing user and continue through the current Google phone-link flow.

If the email does not belong to any user, keep the current Google-first flow: create a pending Google user, ask for phone number, verify OTP, and link the phone.

Follow the existing Auth service layering: router, schemas, use cases, DI, repositories, and docs. Follow the existing Flutter auth repository/controller/model pattern and keep navigation centralized.
