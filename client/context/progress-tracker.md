# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase

- Client foundation, authentication UI, real Auth API wiring, and post-auth navigation shell are complete; next phase is broader backend integration and ride-feature expansion.

## Current Goal

- Keep client context synchronized while expanding real backend integrations across passenger ride booking and driver mode, including the real-time driver Requests tab.
- Move ride-entry, notification-routing, and active-ride orchestration onto a shared lifecycle platform so those decisions stop living in isolated feature widgets.

## Completed

- Flutter scaffold and platform folders were added.
- Shared utilities, theme constants, app text constants, validators, HTTP client, storage helpers, and auth feature structure were added.
- Phone OTP registration flow was added with login, OTP, profile, and post-auth permission routing.
- Google auth setup was added with Google token verification and a dedicated phone-link screen when a phone is required.
- Authenticated `/me` user caching was added so Settings/Profile use saved user display data instead of static demo values.
- `client/lib/data/.gitkeep` was added to preserve the empty data folder.
- Client context documentation and plans folder were introduced.
- Reconstructed feature-spec prompt files were planned for scaffold, design foundation, onboarding, auth gate/login, phone OTP/profile, permissions/home, Google phone linking, and documentation workflow.
- Firebase generated config hardening was added so API-key-bearing generated files are local-only and ignored going forward.
- Post-auth navigation now routes authenticated users through `NavigationMenu` instead of directly to `HomeScreen`.
- Navigation menu active-state design was updated to use a smooth top indicator line instead of a selected pill highlight.
- Navigation menu indicator positioning was refined to use responsive width-based centering, and bottom tab icons were reduced in size.
- Reusable ride search result row was added under `common/widgets/ride`.
- Typed demo ride response models and 10 demo ride records were added under `lib/data/rides`.
- Home search now shows two recent ride destinations from demo data.
- Home banner carousel was added with local banner assets.
- Home service categories were added with local category assets.
- Notification, category, and ride search widget design values were moved into shared utilities without intentional visual changes.
- Client widget structure was cleaned up with reusable widgets moved to `lib/common/widgets`, multi-widget files split, and settings rebuilt from focused components.
- Settings profile edit and `User Info` row now navigate to the personalization profile screen through a reusable right-slide transition.
- A reusable shadcn edit drawer was planned for local profile value edits from personalization profile rows.
- Settings `Privacy & Security` now opens a dedicated Privacy Policy page with expandable mapped policy sections.
- Settings `Notifications` now opens a dedicated timeline-style Notifications page with mapped demo notifications and local category filters.
- Settings `Help & Support` now opens a reference-matched support hub with five placeholder support option subpages.
- Bottom navigation Trips now opens a four-tab ride history page with ongoing, scheduled, canceled, completed, and ride details views.
- Home search now uses a reusable common `SSearchBar` while keeping recent ride rows in the Home feature.
- Passenger map/location foundation was added with Mapbox Flutter SDK, device GPS service, backend location/geospatial repositories, ride tracking WebSocket parsing, reusable map widget, ride search, route preview, and tracking screens.
- Passenger ride search was redesigned as a map-first booking flow with a draggable bottom sheet, backend search, map-pin pickup/dropoff selection, route preview, category/vehicle choices, and hybrid offer creation.
- Passenger ride search map now renders selected pickup/dropoff markers and a connecting route line, falling back to a straight connector when backend route geometry is unavailable.
- Passenger ride search map route rendering now depends on backend route geometry for the displayed route instead of drawing a misleading straight pickup-to-dropoff connector.
- Driver registration entry flow was added from Settings with earning category selection, vehicle selection, Verification `/me` status parsing, and a status checklist.
- Driver registration verification demo mode was added so all `/me` checklist states can be previewed without running the backend.
- Driver registration submit-review CTA and polished verification header layout were added for ready-to-submit checklist states.
- Driver registration step submission pages were implemented with per-step forms, presigned upload handling, realtime selfie capture, and backend-offline demo responses.
- Client screen structure normalization was applied across feature screens so screen files, widgets, subscreens, and content/model files follow one convention.
- Driver-capable accounts can switch between passenger and driver app modes from Settings; driver mode currently shows Drive and Requests starter tabs, a real Earnings tab, and Profile.
- Authentication mocks were removed from the Flutter auth repository; phone OTP, registration, refresh, logout, and `/me` now call the real Auth service.
- Auth local Docker testing now uses backend console OTP mode so OTPs print in auth service logs while WhatsApp remains available outside console mode.
- Existing phone OTP users now log in directly after verification; new phone users still continue to Complete Profile with a `registration_token`.
- Auth profile demographics are persisted: Complete Profile collects email, gender, and DOB, and Profile edits name/email/gender/DOB through Auth.
- Google login now handles verified emails that already exist in Auth: existing email + phone users verify OTP against the saved phone before tokens are issued; existing email + no phone users reuse the current phone-link flow.
- Linked Google accounts with saved phones now also verify OTP against the saved phone before app tokens are issued.
- Passenger ride, route, live tracking, and HYBRID bidding repositories now call real backend HTTP/WebSocket APIs when `SAFARPAY_USE_LOCATION_DEMO_DATA=false`, while preserving demo fixtures when it is true.
- Driver Earnings tab now calls real Payment service data through `GET /api/v1/earnings/me`, with Payment aggregating completed Ride rows, accepted Bidding data, Verification driver stats, wallet balances, commission reservations, and ride payments.
- Payment service exposes a driver-scoped earnings read model and focused tests for the use case and route contract.
- Demo driver earnings seed SQL was added at `scripts/demo/seed_driver_earnings.sql` for the requested driver/rider emails.
- Driver Requests tab is being implemented with real Ride driver request/active ride endpoints, Bidding HYBRID offer support, Location online/GPS streaming, Geospatial route summaries, and an active-trip map state.
- Closed-app ride communication notification recovery is being added so message and voice-call pushes can reopen ride communication with enough call context to survive a cold start.
- Client lifecycle-platform hardening is underway so passenger ride entry, push routing, and active ride state share one lifecycle model instead of scattered conditionals.
- Actionable notification delivery fix (080) resolved closed-app calls and messages FCM payload delivery issues.
- Full-screen native driver requests overlay (081) replaced the top partial floating dialog with a space-optimized full-screen layout.

## In Progress

- Documentation history is being reorganized into feature-first prompt and plan files.
- Firebase generated config is being removed from Git tracking while preserved locally for development.
- Flutter analyzer still reports existing info-level cleanup items in unrelated files.

## Next Up

- Manually test phone OTP and Google phone-link flows on a device or emulator.
- Manually test Google existing-email login on a device: one account with saved phone, one account without phone, and one brand-new Google email.
- Manually test returning Google login on a previously linked account with a saved phone; it should route to OTP before Home.
- Test real phone OTP registration on a physical device using `SAFARPAY_AUTH_BASE_URL=http://<laptop-wifi-ip>:8001/api/v1/auth`.
- Clean existing analyzer info items when the team chooses a lint-cleanup pass.
- Run an end-to-end backend test for passenger HYBRID matching with Ride, Bidding, Location, Geospatial, Kafka, Redis, Auth, and Postgres running.
- Seed `scripts/demo/seed_driver_earnings.sql` into the Docker Postgres database and manually verify the driver Earnings tab with `SAFARPAY_PAYMENT_BASE_URL=http://<laptop-wifi-ip>:8009/api/v1`.
- Add the dedicated full-screen passenger bidding/offers experience after the bottom-sheet live offer state is validated against real drivers.
- Verify the real driver registration submission forms, presigned upload flow, and submit-review readiness with the Verification backend when it is available.
- Restore the real Verification `/me` HTTP call after backend testing is available and remove or disable temporary demo status mode.
- Restore the real Verification submit-review HTTP call after backend testing is available and reload `/me` after successful submission.
- Rotate or restrict the previously exposed Firebase API keys in Google Cloud/Firebase and resolve the GitHub secret-scanning alerts.

## Open Questions

- What exact backend response shape will production Google verification return when phone linking is required?
- Should the client support driver-specific onboarding or remain rider-only for the current phase?
- Should Verification backend expand `VehicleType` beyond `moto`, `economy`, `comfort`, and `freight`, or should the client map display vehicles into those four backend values?
- Which generated platform file changes should be committed, if any, after plugin changes?
- Should grocery booking get a store-selection feature before enabling real `GROCERY` ride creation?

## Architecture Decisions

- Phone OTP is the primary auth path; Google is a secondary provider.
- Google phone linking is a dedicated screen, not a modified login-screen state.
- Google existing-email login uses a masked-phone OTP step; the full saved phone is never returned to Flutter.
- Any Google login that resolves to an Auth user with a saved phone must verify OTP before session creation, including already-linked Google accounts.
- OTP verification remains centralized in `OtpScreen` and `SOtpController`.
- Tokens are persisted only through `STokenStorage`.
- App copy remains centralized in `STexts`.
- Empty source folders that matter to architecture are preserved with `.gitkeep`.
- `NavigationMenu` is the authenticated app shell; `HomeScreen` is only the first tab.
- Navigation menu active state is represented by primary icon/label color and a custom animated top line.
- Navigation menu top indicator positioning must be calculated from tab width instead of hard-coded alignment values.
- Shared ride UI components live in `lib/common/widgets/ride` when they are not owned by one screen.
- Ride demo data mirrors backend response contracts until live ride APIs are integrated.
- Home carousel uses local banner assets and app sizing/radius tokens.
- Home service categories are static local UI until service destination screens are planned.
- Shared widget styling should use `SColors`, `SOpacities`, `SSizes`, `STexts`, and `SHelperFunctions` instead of local literals.
- Reusable widgets belong in `lib/common/widgets`; screen-local widgets should live in the owning screen's `widgets/` folder with one primary widget per file.
- Reusable non-auth page transitions live in `lib/common/navigation`.
- Reusable shadcn drawers live in `lib/common/widgets/drawers` and use the local shadcn-ui-flutter skill docs.
- Settings legal and privacy content should render from typed mapped content files so copy can be updated without rewriting page layout.
- Settings notification feeds should render from typed mapped demo content until backend notification APIs are integrated.
- Help & Support option rows should remain a simple support hub until live support workflows are planned.
- Trips list and details screens should consume backend-aligned ride DTOs and avoid backend mutation flows until ride APIs are connected.
- Reusable search bar UI should stay under `lib/common/widgets/searchbar`, with feature-owned result rendering kept out of the shared widget.
- Mapbox client usage is limited to native map rendering; geocoding, route calculation, and ETA logic stay behind backend services.
- Passenger v1 uses foreground location only and does not persist raw GPS history locally.
- Driver registration reads the canonical state from Verification `/me`; display vehicle choices remain separate from backend verification enum values until submission forms are implemented.
- Vehicle verification belongs to the physical vehicle; adding that vehicle to another driver service requires explicit user consent before the client creates the service capability.
- Passenger ride booking uses a map-first shell with backend-mediated search/routes and HYBRID ride creation for inDrive-style offers.
- Driver mode is a local UI preference stored separately from auth role; auth roles `driver` and `admin` gate access to the switch.

## Session Notes

- Existing local dirty files include auth flow code changes, platform generated plugin registrant files, `code.md`, `PAYMENT_SERVICE_FLOW.md`, `SafarPay.iml`, and `client/AGENTS.md`.
- `flutter analyze --no-pub` was run after the Google phone-link work and only reported existing info-level items outside the new screen.
- During the client structure cleanup, `dart format` and `flutter analyze --no-pub` timed out in this environment; targeted source scans were used to verify widget-file structure and stale-name cleanup.
- Future agents should read `client/AGENTS.md` and then the context files before changing client code.
- The client structure cleanup added `context/feature-specs/017-client-structure-cleanup.md` and `plans/018-client-structure-cleanup-plan.md`.
- Settings user-info navigation added `context/feature-specs/018-settings-user-info-navigation.md` and `plans/019-settings-user-info-navigation-plan.md`.
- Common edit drawer work added `context/feature-specs/019-common-edit-drawer.md` and `plans/020-common-edit-drawer-plan.md`.
- Privacy Policy page work added `context/feature-specs/020-privacy-policy-page.md` and `plans/021-privacy-policy-page-plan.md`.
- Notifications page work added `context/feature-specs/021-notifications-page.md` and `plans/022-notifications-page-plan.md`.
- Help & Support page work added `context/feature-specs/022-help-support-page.md` and `plans/023-help-support-page-plan.md`.
- Trips page work added `context/feature-specs/023-rides-trips-page.md` and `plans/024-rides-trips-page-plan.md`.
- Common search bar work added `context/feature-specs/024-common-searchbar-widget.md` and `plans/025-common-searchbar-widget-plan.md`.
- Passenger map/location work added `context/feature-specs/025-passenger-map-location-tracking.md` and `plans/026-passenger-map-location-tracking-plan.md`.
- Driver registration work added `context/feature-specs/026-driver-registration-flow.md` and `plans/027-driver-registration-flow-plan.md`.
- Driver verification demo status work added `context/feature-specs/027-driver-verification-demo-status.md` and `plans/028-driver-verification-demo-status-plan.md`.
- Driver submit-review/header polish work added `context/feature-specs/028-driver-submit-review-and-header-polish.md` and `plans/029-driver-submit-review-and-header-polish-plan.md`.
- Driver registration step submission page work added `context/feature-specs/029-driver-registration-step-submission-pages.md` and `plans/030-driver-registration-step-submission-pages-plan.md`.
- Client screen structure normalization work added `context/feature-specs/030-client-screen-structure-normalization.md` and `plans/031-client-screen-structure-normalization-plan.md`.
- Branch split workflow work added `context/feature-specs/031-branch-split-and-pr-merge.md` and updated `plans/900-branch-split-and-merge-plan.md`.
- Map-first passenger booking work added `context/feature-specs/032-map-first-passenger-booking-flow.md` and `plans/032-map-first-passenger-booking-flow-plan.md`.
- Temporary location demo data mode added `context/feature-specs/033-location-demo-data-mode.md` and `plans/033-location-demo-data-mode-plan.md`; restore real repository HTTP calls when backend services are available.
- Ride and Bidding backend integration work added `context/feature-specs/034-ride-bidding-api-websocket-integration.md` and `plans/034-ride-bidding-api-websocket-integration-plan.md`; use `SAFARPAY_USE_LOCATION_DEMO_DATA=false` to exercise real backend HTTP and WebSocket paths.
- Ride and Bidding demo runtime mode added `context/feature-specs/035-ride-bidding-demo-runtime-mode.md` and `plans/035-ride-bidding-demo-runtime-mode-plan.md`; repositories and sockets currently return demo data directly while real backend fetch/connect blocks are commented in place.
- Home category booking entry work added `context/feature-specs/036-home-category-to-ride-search.md` and `plans/036-home-category-to-ride-search-plan.md`; category tiles now open Ride Search with the tapped category preselected.
- Terms & Conditions page work added `context/feature-specs/037-terms-conditions-page.md` and `plans/037-terms-conditions-page-plan.md`; Help & Support now renders local policy categories and expandable detail pages from typed static data.
- FAQ page work added `context/feature-specs/038-faqs-page.md` and `plans/038-faqs-page-plan.md`; Help & Support now renders local FAQ categories, popular articles, and article details from typed static data.
- FAQ search/category interaction work added `context/feature-specs/039-faq-search-and-category-interactions.md` and `plans/039-faq-search-and-category-interactions-plan.md`; search and category taps now filter local FAQ articles and the `View All Articles` button remains removed.
- Something Else support ticket work added `context/feature-specs/040-something-else-support-ticket.md` and `plans/040-something-else-support-ticket-plan.md`; the repository currently returns a demo response while the future Gateway `POST /support/tickets` call remains documented in code.
- Contact Us page work added `context/feature-specs/041-contact-us-page.md` and `plans/041-contact-us-page-plan.md`; support phone/email now live in `STexts` and the screen renders local contact/social actions.
- Auth user cache work added `context/feature-specs/043-auth-user-cache.md` and `plans/043-auth-user-cache-plan.md`; cached user profile data is UI-only and `/me` remains authoritative.
- Driver mode switch work added `context/feature-specs/044-driver-mode-switch.md` and `plans/044-driver-mode-switch-plan.md`; auth `role` gates access while local app mode controls the active shell.
- Real Auth API and console OTP work added `context/feature-specs/045-real-auth-api-and-console-otp.md` and `plans/045-real-auth-api-and-console-otp-plan.md`; Flutter auth mocks are removed and Docker auth prints OTP codes in console mode.
- Existing phone login branching work added `context/feature-specs/046-existing-phone-login.md` and `plans/046-existing-phone-login-plan.md`; `/otp/verify` now returns `next_step` so existing phone users receive tokens while new users receive `registration_token`.
- Auth profile demographics work added `context/feature-specs/047-auth-profile-demographics.md` and `plans/047-auth-profile-demographics-plan.md`; Auth owns email/gender/DOB persistence and phone remains read-only in Profile.
- Google existing-email auth work added `context/feature-specs/048-google-existing-email-auth.md` and `plans/048-google-existing-email-auth-plan.md`; Auth now branches Google login by existing account/email state.
- Google linked-phone OTP work added `context/feature-specs/049-google-linked-phone-otp-auth.md` and `plans/049-google-linked-phone-otp-auth-plan.md`; already-linked Google accounts with saved phones now use the same saved-phone OTP gate before tokens.
- Driver vehicle taxonomy work added `context/feature-specs/050-driver-vehicle-taxonomy.md` and `plans/050-driver-vehicle-taxonomy-plan.md`; verification and ride now use canonical physical vehicle values while service type represents driver work capability.
- Driver vehicle service reuse work added `context/feature-specs/051-driver-vehicle-service-reuse.md` and `plans/051-driver-vehicle-service-reuse-plan.md`; vehicle selection now uses real Verification state and reuses existing physical vehicles across services.
- Driver vehicle service consent work added `context/feature-specs/052-driver-vehicle-service-consent.md` and `plans/052-driver-vehicle-service-consent-plan.md`; existing vehicles must be confirmed by the driver before attaching them to another service.
- Ride backend client integration work added `context/feature-specs/054-ride-backend-client-integration.md` and `plans/054-ride-backend-client-integration-plan.md`; passenger ride, geospatial, location, and HYBRID bidding repositories now use real backend paths when demo mode is disabled.
- Driver earnings real-data work added `context/feature-specs/055-driver-earnings-real-data.md` and `plans/055-driver-earnings-real-data-plan.md`; Payment now exposes driver earnings and Flutter driver mode renders a real Earnings tab.
- Passenger ride options work added `context/feature-specs/057-passenger-ride-options-bottom-sheet.md` and `plans/057-passenger-ride-options-bottom-sheet-plan.md`; the ride search bottom sheet now collects backend-aligned fixed/hybrid, payment, city, intercity, courier, and freight options through a progressive flow.
- Complete ride lifecycle hardening work added `context/feature-specs/058-complete-ride-lifecycle-hardening.md` and `plans/058-complete-ride-lifecycle-hardening-plan.md`; Bidding now has the internal Payment URL contract, client token refresh is single-flight, websocket connections request fresh tokens, and lifecycle-critical backend/client checks pass.
- Complete ride lifecycle E2E verification work added `context/feature-specs/059-complete-ride-lifecycle-e2e-verification.md`, `plans/059-complete-ride-lifecycle-e2e-verification-plan.md`, and `tests/e2e/test_complete_ride_lifecycle.py`; the harness is opt-in with `SAFARPAY_RUN_DOCKER_E2E=1` and verifies fixed plus hybrid lifecycle completion across Ride, Bidding, Location, Verification, and Payment against the Docker stack.
- Shared ride lifecycle primitives, a centralized passenger ride-entry policy, a shared notification route parser, and an app-level ride lifecycle coordinator were added under `lib/features/rides`.
- Shared ride destinations and navigation helpers now own ride details, fixed waiting, hybrid matching, live tracking, communication, and driver request entry from lifecycle-owned flows.
- Trips ongoing ride navigation now uses the shared lifecycle policy instead of hard-coded hybrid/fixed/tracking branches in the list widget.
- Push notification routing now resolves a shared notification route intent before opening driver requests, ride tracking, or ride communication.
- Passenger ride tracking and driver requests now publish active lifecycle state into the shared coordinator.
- Booking acceptance, pending matching recovery, ride preview completion, and the ride communication FAB now use the shared destination helpers instead of direct screen pushes.
- Phase 3 realtime/runtime orchestration was added with a shared `SRideRealtimeOrchestrator` that owns lifecycle-stage rules for passenger ride sockets, passenger live location sockets, hybrid bidding sockets, ride communication sockets, driver marketplace suppression, and driver foreground GPS runtime.
- App lifecycle resume recovery now refreshes HTTP snapshots first and then reattaches live channels in passenger tracking, passenger hybrid matching, driver requests, and ride communication controllers.
- Phase 4A runtime diagnostics were added with `SRuntimeModeConfig` and `SRuntimeDiagnosticsController`; diagnostics now expose app lifecycle state, demo-vs-real location mode, active passenger/driver ride lifecycle, realtime channel flags, and driver foreground runtime state.
- Runtime repository extraction was split into `073-runtime-repository-extraction` so demo-vs-real implementation separation can happen repository family by repository family without destabilizing the ride lifecycle.
- Runtime repository extraction Phase 073 completed for Location, Geospatial, Bidding, Ride, and socket repository families; Phase 074 completed the dedicated `SRideRepository` method extraction into demo and HTTP delegates while preserving static booking payload builders.
- Android driver urgent ride alerts were added in `075-android-driver-urgent-ride-alerts`: driver ride-job notifications now carry `driver_ride_request`, FCM Android payloads use urgent ride-alert settings, Flutter foreground/background handlers show urgent local ride notifications, and driver online mode refreshes push token registration with `driver_id`.
- Enterprise notification delivery matrix work was added in `076-enterprise-notification-delivery-matrix`: driver marketplace ride requests now have Android overlay support gated by Display over other apps, communication calls use call-channel notification actions, data-only communication payloads route correctly, and FCM marks communication calls as urgent `ride_calls` notifications.
- Actionable notification delivery fix work was completed in `080-actionable-notification-delivery-fix` to restore standard background/closed visual alerts for calls and chat messages.
- Full-screen native driver overlay work was completed in `081-full-screen-overlay` to convert the native request alerts to full-screen layouts.
# 2026-05-25 - Ride Communication Chat And Calls

- Added ride-scoped communication prompt and plan for accepted-before-start rides.
- Integrated `services/communication` by-ride conversation lookup.
- Added Flutter communication data/socket/controller/UI structure for chat, image attachments, voice notes, and WebRTC voice calls.
- Added chat entry buttons to passenger Live Ride and driver active ride screens before trip start.
# 2026-05-27 - Closed-App Ride Communication Notifications

- Added the closed-app ride communication notification prompt and implementation plan.
- Communication message, media, and call events are being enriched with ride and recipient metadata so notification routing can work when the app is backgrounded or killed.
- Ride communication is gaining call recovery by `call_id` so notification taps can reopen the pending call state after a cold start.
# 2026-05-27 - Enterprise Client Lifecycle Platform

- Added the lifecycle-platform prompt and implementation plan.
- Added shared ride lifecycle and notification route policy modules under `lib/features/rides`.
- Trips navigation, push routing, driver active ride state, and passenger tracking state now use the shared lifecycle platform as the first extraction point for wider client orchestration.
- Added the phase-split prompt/plan docs for `070`, `071`, and `072`.
- Implemented Phase 2 by adding shared ride destinations and moving lifecycle-owned ride entry and recovery flows onto them.
# 2026-05-25 - Passenger Ride UX And Trips Real Data

- Planned real backend-backed Trips, fresh ride details, improved booking details, and improved ride communication/call UI.
- Scope is tracked in `client/context/feature-specs/061-passenger-ride-ux-and-trips-real-data.md`.
- Implementation plan is tracked in `client/plans/061-passenger-ride-ux-and-trips-real-data-plan.md`.

# 2026-05-28 - Actionable Notifications, Driver Overlay, Edit Destination & Cancel Ride

- Actionable notification delivery fix work added `client/context/feature-specs/080-actionable-notification-delivery-fix.md` and `client/plans/080-actionable-notification-delivery-fix-plan.md`.
- Full-screen native overlay work added `client/context/feature-specs/081-full-screen-overlay.md` and `client/plans/081-full-screen-overlay-plan.md`.
- Edit Destination and Cancel Ride work added `client/context/feature-specs/082-edit-destination-and-cancel-ride.md` and `client/plans/082-edit-destination-and-cancel-ride-plan.md`.

# 2026-05-29 - Login Page UI Refactoring

- Login Page UI Refactoring work added `client/context/feature-specs/083-login-ui-refactoring.md` and `client/plans/083-login-ui-refactoring-plan.md`.
