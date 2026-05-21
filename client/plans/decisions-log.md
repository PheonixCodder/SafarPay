# Decisions Log

Permanent record of decisions that affect product scope, architecture, auth behavior, storage, security, deployment, or workflow.

## Decisions

### Auth User Cache Is UI-Only

- Date: 2026-05-19
- Decision: Cache the authenticated `/me` user locally for Settings/Profile display, while keeping tokens in secure storage and treating backend `/me` as authoritative for role, active state, verification state, and onboarding state.
- Rationale: The app needs real user display data after authentication, but local cache must not become trusted auth or authorization state.

### Passenger Map-First Hybrid Booking

- Date: 2026-05-18
- Decision: Passenger ride booking opens as a map-first draggable-sheet flow and creates non-fixed rides with backend `HYBRID` pricing for offer-style matching.
- Rationale: The product direction matches inDrive-style passenger offers while preserving SafarPay's backend boundaries: Flutter renders maps and captures intent, while backend services own geocoding, routing, ride creation, bidding sessions, and authorization.

### Passenger Bidding Session Contract

- Date: 2026-05-18
- Decision: Production live offer tracking requires Ride creation or the passenger Ride WebSocket to expose `bidding_session_id` for non-fixed rides.
- Rationale: The current Bidding API reads sessions by session id, but the client starts from a newly created ride. A clear ride-to-session contract avoids fragile polling or fake live bid state.

### Driver Registration Verification State

- Date: 2026-05-17
- Decision: The Flutter driver registration checklist reads canonical state from Verification service `GET /api/v1/verification/me`.
- Rationale: The backend already aggregates identity, license, selfie, vehicle, rejection, under-review, and verified states. The client should render that contract instead of duplicating backend review logic.

### Driver Registration Vehicle Display Mapping

- Date: 2026-05-17
- Decision: Driver registration earning-category vehicle options are display choices only until the detailed vehicle submission form is implemented.
- Rationale: The current Verification backend vehicle enum supports `moto`, `economy`, `comfort`, and `freight`, while the desired client UI includes vehicles such as Rickshaw, Van, Pickup, Mini truck, and Truck.

### Driver Verification Demo Status Mode

- Date: 2026-05-17
- Decision: Temporarily return backend-shaped demo Verification `/me` responses from the driver verification repository while the backend is unavailable.
- Rationale: Keeping demo data at the repository boundary lets the status screen and controller exercise the same production data flow while making every UI state testable offline.

### Driver Verification Submit Review Eligibility

- Date: 2026-05-17
- Decision: Show the driver `Submit for Review` action only when all four Verification `/me` groups are `pending` and `overall_status` is `pending`.
- Rationale: The backend does not expose a separate ready flag. The grouped `/me` contract already proves whether identity, license, selfie, and vehicle information have all been submitted.

### Driver Registration Presigned Upload Flow

- Date: 2026-05-17
- Decision: Each driver registration step first posts metadata to the Verification service, then uploads images to the exact presigned PUT URLs returned for that step.
- Rationale: The backend owns document keys, storage policy, and review state. The client should not invent file keys or upload destinations.

### Driver Registration Vehicle Type Mapping

- Date: 2026-05-17
- Decision: Client display vehicles map to the current Verification backend enum values: motorcycle to `moto`, freight-class vehicles to `freight`, and standard passenger vehicles to `economy` unless the form explicitly selects `comfort`.
- Rationale: The backend currently accepts only `moto`, `economy`, `comfort`, and `freight`, while the UI uses more specific vehicle labels.

### Client Screen Folder Convention

- Date: 2026-05-17
- Decision: Feature screens use one folder per screen, one main screen file, screen-local widgets under `widgets/`, and owned subscreens under `screens/`.
- Rationale: The previous tree mixed root screen files, widgets, content files, and subscreens inconsistently across features. A single convention reduces navigation/import confusion and keeps widget ownership explicit.

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

### 0027 - Keep search bar UI common and result composition feature-owned

- **Decision**: Move the reusable search bar surface to `lib/common/widgets/searchbar` and keep Home recent ride rows inside the Home feature.
- **Reason**: The search bar visual primitive will be reused across ride flows, while result data, demo rides, and destination rows are feature-specific composition.

### 0028 - Keep Mapbox APIs backend-mediated

- **Decision**: The Flutter client uses Mapbox only for native map rendering. Geocoding, reverse geocoding, route calculation, ETA enrichment, and pickup validation are called through SafarPay backend services.
- **Reason**: Backend mediation keeps protected Mapbox capabilities, authorization, caching, rate limiting, and audit behavior centralized while the passenger app stays focused on UX and live state rendering.

### 0029 - Passenger location starts as foreground-only

- **Decision**: Passenger map and tracking flows use foreground device location only and do not persist raw GPS history locally.
- **Reason**: Foreground location is enough for pickup selection and active ride UI in v1. Background location has privacy, platform, and product implications that should be handled in a separate approved feature plan.

### 0030 - Split mixed client work through a safety snapshot

- **Decision**: Before creating feature PRs from the current mixed client worktree, create a local safety branch named `codex/safety-unsplit-client-work` and restore explicit path groups from that snapshot into each PR branch.
- **Reason**: The worktree contains multiple independent client features and refactors. A safety snapshot preserves all code while allowing each PR to be reviewed and merged with a narrow scope.

### 0031 - Keep screen-local widgets under owning screen folders

- **Decision**: Home screen widgets now live under `lib/features/home/screens/home/widgets`, and the old `lib/features/home/screens/widgets` files are removed.
- **Reason**: Screen-local widgets should stay with the screen that owns them, matching the one-screen-file plus widgets-folder convention used across the client.

### 0032 - Use temporary demo data for passenger location UI testing

- **Decision**: While backend services are unavailable, Location, Geospatial, Ride, and Bidding repositories return centralized demo fixtures from `lib/features/location/data/demo`.
- **Reason**: The map-first passenger booking UI needs to remain testable without changing the production contract. Real backend fetch blocks stay commented in place for quick restoration, and the passenger offer flow remains `HYBRID`.

### 0033 - Gate demo location flow behind a compile-time switch

- **Decision**: Use `SAFARPAY_USE_LOCATION_DEMO_DATA` to choose between centralized demo fixtures and real Location, Geospatial, Ride, and Bidding backend calls.
- **Reason**: The UI still needs to run without backend services, but the production code paths should stay wired and testable without manual commenting or file edits.

### 0034 - Keep Ride, Bidding, and Location WebSockets separate

- **Decision**: Use separate repositories for Ride lifecycle WebSockets, Bidding negotiation WebSockets, and Location live-coordinate WebSockets.
- **Reason**: These channels have different backend services, auth paths, event shapes, and ownership. Keeping them separate prevents ride state, bids, and GPS updates from becoming coupled in one socket abstraction.

### 0035 - Force ride and bidding runtime paths to demo while backend is unavailable

- **Decision**: Ride, Bidding, Location, Geospatial, and live socket repositories now return deterministic demo responses directly, with real HTTP/WebSocket code preserved as comments beside each method.
- **Reason**: Backend services are not currently runnable, but the map-first passenger booking, matching, and tracking UI still needs full-flow data for testing. Preserving the real blocks keeps the restore path explicit.

### 0036 - Home categories deep-link into passenger booking categories

- **Decision**: Home service category tiles open `RideSearchScreen` with the matching `SPassengerServiceCategory` selected.
- **Reason**: The Home category grid is a service entry surface; preserving the selected category through navigation keeps the booking flow consistent with the user's tap intent.

### 0037 - Separate auth role capability from local app mode

- **Decision**: Store passenger/driver mode as a local `GetStorage` UI preference, gated by cached `/me` roles `driver` and `admin`.
- **Reason**: Auth `role` describes what the account is allowed to access, while app mode describes which authenticated shell is currently active. Keeping them separate lets approved drivers switch views without changing backend identity state.

### 0038 - Use backend console OTP for local auth testing

- **Decision**: Remove Flutter auth mocks and use the real Docker Auth service. Local Docker auth selects `AUTH_OTP_DELIVERY_MODE=console`, which logs OTPs instead of sending WhatsApp messages.
- **Reason**: Phone OTP registration should exercise real backend persistence, verification, tokens, and `/me` behavior even when WhatsApp Business API credentials are unavailable locally.

### 0039 - Let OTP verification choose login versus profile completion

- **Decision**: `/otp/verify` returns an explicit `next_step`: existing phone users receive tokens, new phone users receive `registration_token`, and Google phone linking uses `purpose=phone_link`.
- **Reason**: The OTP screen is shared, but existing users should not be forced through Complete Profile again. Making the backend return the next step keeps account existence authoritative in Auth service instead of duplicated in Flutter.

### 0040 - Persist editable demographics in Auth profiles

- **Decision**: Store `email`, `gender`, and `date_of_birth` on `auth.users`; register collects them, `/me` returns them, and `PATCH /me` updates name, email, gender, and DOB while phone remains read-only.
- **Reason**: These fields are account profile data owned by Auth. Keeping phone immutable from Profile preserves the OTP-verified identity boundary while allowing normal profile edits through one authenticated route.

### 0041 - Verify existing Google email accounts with saved-phone OTP

- **Decision**: When Google email matches an existing Auth user with a phone, Auth sends OTP to the saved phone and returns a masked phone plus a short-lived Google login token; normal tokens are issued only after OTP verification.
- **Reason**: Google verifies email ownership, but the saved phone remains the app identity anchor. OTP prevents a Google login from silently taking over an existing phone-backed account while avoiding duplicate users.

### 0042 - Require saved-phone OTP for linked Google logins

- **Decision**: When a Google account is already linked to an Auth user and that user has a saved phone, `/google/verify-token` sends OTP and returns `verify_existing_phone` instead of issuing tokens immediately.
- **Reason**: The saved phone remains the account possession check even for returning Google users. This keeps linked-account Google login consistent with existing-email Google login and prevents bypassing phone verification before session creation.

### 0043 - Normalize driver services and vehicle taxonomy

- **Decision**: Use five service types for work capabilities and seven canonical vehicle types for physical vehicles across driver registration, ride requests, and matching.
- **Reason**: Verification buckets like `economy`/`freight` and ride body styles like `SEDAN`/`HATCHBACK` created ambiguous matching rules. Canonical `VehicleType` plus service capabilities keeps registration, dispatch, and future backend matching coherent.

### 0044 - Reuse driver vehicles across services

- **Decision**: A driver reuses one physical vehicle per vehicle type and attaches additional services through `driver_service_capabilities` instead of creating duplicate vehicle rows.
- **Reason**: A Car used for City Ride, Intercity, and Courier is the same asset and should share documents, verification state, and plate identity while exposing service-specific capability state to matching and UI flows.
