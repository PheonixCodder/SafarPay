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

### 0010 - Keep Firebase generated config out of Git

- **Decision**: Stop tracking `lib/firebase_options.dart`, `android/app/google-services.json`, and Apple `GoogleService-Info.plist` files.
- **Reason**: Firebase client API keys are not traditional private server secrets, but GitHub secret scanning flags them and they should be generated locally, restricted in Google Cloud/Firebase, and rotated when exposed.

### 0011 - Route post-auth users through NavigationMenu

- **Decision**: Send authenticated users with completed permissions to `NavigationMenu` instead of directly to `HomeScreen`.
- **Reason**: The main app needs one authenticated shell that owns Home, Trips, Rent, and Profile navigation consistently across phone OTP, Google auth, permissions completion, and already-authenticated app launch.

### 0012 - Use custom active indicator for NavigationMenu

- **Decision**: Replace Material `NavigationBar`'s selected pill treatment with a custom bottom bar that uses active icon/label coloring and an animated top indicator line.
- **Reason**: The product reference requires a cleaner active state where the line moves smoothly between tabs without the built-in Material highlight.

### 0013 - Calculate NavigationMenu indicator position from tab width

- **Decision**: Center the active indicator using the actual bottom-bar width divided by the number of tabs instead of hard-coded `Alignment` values.
- **Reason**: Hard-coded alignment values drift on real layouts; width-based positioning keeps Home, Trips, Rent, and Profile centered consistently across devices.

### 0014 - Use upright typography only

- **Decision**: Do not use or register italic font faces in the Flutter client.
- **Reason**: Italic SF Pro assets caused themed text weights such as `headlineMedium` to render with a curved/italic appearance. SafarPay's visual language should use upright typography only; missing weights should wait for matching upright font files instead of falling back to italic assets.

### 0015 - Place reusable ride rows under common widgets

- **Decision**: Store reusable ride search result UI in `lib/common/widgets/ride`.
- **Reason**: Location result rows can be reused by search, booking, and ride flows, so they should not be owned by a single feature screen.

### 0016 - Mirror backend ride response contracts in client data models

- **Decision**: Define typed Dart ride response models and enums under `lib/data/rides` that preserve backend enum wire values and JSON field names.
- **Reason**: The frontend can build against realistic demo data now while keeping a clean path to future backend integration.

### 0017 - Use local banner assets for the home carousel

- **Decision**: Render the home carousel from local assets declared in `SImages` and `pubspec.yaml`.
- **Reason**: Local banners keep the home experience available offline during early client development and avoid adding remote media loading behavior before product content is finalized.

### 0018 - Keep home service categories static until service routing is planned

- **Decision**: Render Groceries, City rides, City to City, Couriers, and Freight as static home tiles backed by local assets and centralized text constants.
- **Reason**: The home screen needs the service discovery surface now, but destination screens and service-specific routes are not planned yet.

### 0019 - Centralize upgraded widget design values in utils

- **Decision**: Move notification, category, and ride search result dimensions, opacity values, and display strings into `lib/utils`.
- **Reason**: The upgraded visual design should remain stable while keeping shared widgets maintainable and consistent with SafarPay's utility-first Flutter style.

### 0020 - Split reusable widgets into focused files

- **Decision**: Keep one primary widget class per Dart file where practical, move reusable UI primitives into `lib/common/widgets`, and keep screen-only widgets under the owning screen's `widgets/` folder.
- **Reason**: The client had accumulated reusable widgets inside feature files and multiple widget classes per file. Focused files and common widget ownership make future ride, settings, and navigation work easier to change without altering the current design.

### 0021 - Use common right-slide route for personalization profile navigation

- **Decision**: Open the personalization `ProfileScreen` from Settings through a reusable right-slide route helper under `lib/common/navigation`.
- **Reason**: Settings profile navigation needs a polished page overlap transition, and keeping the route helper common allows future screens to reuse the same behavior without duplicating `PageRouteBuilder` code.

### 0022 - Use shadcn sheet for reusable local edit drawers

- **Decision**: Add `shadcn_ui` and use a common right-side `ShadSheet` drawer for editing existing values in settings/profile flows.
- **Reason**: Existing-value edits need a focused contextual surface that can be reused across submenu pages while keeping the current profile screen and backend boundaries unchanged.

### 0023 - Render Settings privacy content from mapped sections

- **Decision**: Open Privacy Policy from Settings as a personalization subpage and render policy copy from typed mapped section data.
- **Reason**: Legal/privacy copy will change over time, so the page layout should stay stable while policy content can be edited in one content file.

### 0024 - Use a timeline feed for Settings notifications

- **Decision**: Open Notifications from Settings as a personalization subpage and render demo notifications as a timeline feed with local filters.
- **Reason**: Ride-hailing notifications are time-based updates; a timeline feed feels more professional and less boxy than a category-card grid.

### 0025 - Match the reference layout for Help & Support

- **Decision**: Open Help & Support from Settings as a primary-header support hub with a scooter illustration and simple option rows.
- **Reason**: The supplied reference is specific; matching it closely keeps support navigation familiar while the destination workflows remain placeholder subpages.

### 0026 - Use segmented ride lists for Trips

- **Decision**: Replace the Trips placeholder with a four-tab ride operations page backed by `RideResponse` demo data.
- **Reason**: Trips are state-based operational records, so a segmented list keeps ongoing, scheduled, canceled, and completed rides scannable without a box-heavy dashboard layout.
