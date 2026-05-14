# Decisions Log

Permanent record of decisions that affect product scope, architecture, auth behavior, storage, security, deployment, or workflow.

## Decisions

### 0001 - Use feature-first Flutter structure

- **Decision**: Keep client code organized under `lib/features/<feature>` with shared utilities in `lib/utils` and reusable widgets in `lib/common`.
- **Reason**: This matches the existing auth feature layout and keeps UI, controllers, repositories, and models grouped by product area.

### 0002 - Use GetX for auth flow state and navigation helpers

- **Decision**: Continue using GetX controllers and `SAuthNavigation` for auth flow transitions.
- **Reason**: Existing onboarding, login, OTP, profile, and permissions flows already use GetX patterns.

### 0003 - Keep phone OTP as the primary auth path

- **Decision**: Phone OTP remains the primary auth entrypoint; Google is a secondary provider.
- **Reason**: SafarPay backend supports phone-first registration and optional Google account linking.

### 0004 - Split Google phone linking into its own screen

- **Decision**: Route Google users who require phone linking to `GoogleOtpProfileScreen` instead of changing state inside `LoginScreen`.
- **Reason**: It avoids keeping the Google button visible after Google verification and makes the flow clearer.

### 0005 - Preserve intentional empty source folders with `.gitkeep`

- **Decision**: Use `.gitkeep` for empty source folders such as `client/lib/data`.
- **Reason**: Git does not track empty directories.

### 0006 - Maintain context and plan docs in the client app

- **Decision**: Store client-specific context in `client/context` and implementation plans in `client/plans`.
- **Reason**: Future code changes should be traceable to prompts, decisions, and implementation plans.

### 0007 - Store reconstructed prompts per feature

- **Decision**: Keep prompts that would reproduce current code under `client/context/feature-specs`.
- **Reason**: The app history should be explainable from prompts, plans, and context, not only from source files.

### 0008 - Number product plans before operational Git plans

- **Decision**: Product and feature plans use `000-*` through `008-*`; branch and recovery operations use the `900-*` range.
- **Reason**: Future agents should see app-building history before repository-maintenance history.

### 0009 - Treat auth as UI/mock complete, not backend complete

- **Decision**: Mark onboarding, login, phone OTP, profile, permissions, home, and Google phone-link flows as complete for current client UI and mocked repository behavior.
- **Reason**: The real backend endpoint integration is still represented by commented API calls and mock repository implementations.
