# Architecture Context

## Stack

| Layer | Technology | Role |
| --- | --- | --- |
| Framework | Flutter + Dart | Mobile UI and app runtime |
| State | GetX | Controllers, reactive state, and simple navigation coordination |
| Navigation | Flutter Navigator via `SAuthNavigation`, Get context, and `NavigationMenu` | Auth flow transitions and post-auth tab shell |
| Local preferences | `get_storage` | Lightweight app flags such as permissions completion |
| Secure storage | `flutter_secure_storage` | Access and refresh tokens |
| Auth providers | Phone OTP, Google Sign-In, Firebase Core | Client-side auth entrypoints and platform setup |
| HTTP | `http` through `SHttpClient` | Backend API communication |
| Maps | Mapbox Maps Flutter SDK | Native Android/iOS passenger map rendering |
| Device location | `geolocator` + `permission_handler` | Foreground passenger GPS for pickup and live ride context |
| Realtime | `web_socket_channel` | Passenger ride tracking and bidding WebSocket consumption |
| Driver verification | Verification service HTTP APIs + presigned document uploads | Driver registration status, KYC step submissions, and direct upload to backend-issued object storage URLs |
| UI assets | Local fonts, images, logos, icons | Branded client experience |
| UI components | Material widgets, GetX shell, and `shadcn_ui` | Native Flutter UI with reusable shadcn overlays where planned |
| Documentation | `client/context`, `client/context/feature-specs`, `client/plans` | Source of truth for prompts, plans, decisions, and progress |

## Driver Registration Taxonomy

- Driver service capability uses the backend service type contract: `CITY_RIDE`, `INTERCITY`, `FREIGHT`, `COURIER`, `GROCERY`.
- Driver vehicle registration uses the canonical physical vehicle contract: `CAR`, `MOTORCYCLE`, `RICKSHAW`, `VAN`, `PICKUP`, `MINI_TRUCK`, `TRUCK`.
- Passenger `ServiceCategory` remains a product/tier label and must not be used as driver service capability or vehicle type.
- `PricingMode` remains pricing behavior only.

## System Boundaries

- `lib/app.dart` - app-level theme and root widget setup.
- `lib/main.dart` - Flutter/Firebase/bootstrap entrypoint.
- `lib/common/` - shared widgets and layout styles that are not feature-specific; reusable widgets should live here instead of inside feature folders.
- `lib/common/navigation/` - reusable Navigator route transitions and navigation helpers shared across features.
- `lib/common/widgets/navigation/` - shared bottom navigation shell widgets and placeholder tab screens.
- `lib/common/widgets/containers/` - shared decorative containers and header surfaces.
- `lib/common/widgets/images/` - shared image presentation widgets.
- `lib/common/widgets/drawers/` - reusable contextual drawers and sheets for editing existing data.
- `lib/common/widgets/searchbar/` - reusable presentational search bar widgets shared by feature screens.
- `lib/common/widgets/ride/` - reusable ride UI building blocks shared across search, booking, and ride flows.
- `lib/common/widgets/maps/` - reusable Mapbox-backed passenger map widgets and map marker presentation models.
- `lib/data/` - shared DTOs, demo data, and future client-side data abstractions.
- `lib/data/rides/` - backend-aligned ride response models, proof/nearby-driver DTOs, and demo ride data for UI development before live API integration.
- `lib/features/authentication/` - onboarding, login, OTP, profile completion, permissions, auth models, repository, and auth navigation helpers.
- `lib/features/home/` - post-auth starter home experience, using screen folders with screen-local widgets.
- `lib/features/location/` - passenger location, geospatial, map-first ride booking, route preview, hybrid offers, and live ride tracking client layer, with each screen isolated in its own screen folder.
- `lib/features/personalization/` - settings and profile-facing personalization surfaces.
- `lib/features/personalization/screens/driver_registration/` - Settings-launched driver onboarding entry, earning category and vehicle selection, Verification `/me` status rendering, KYC step forms, and presigned document upload orchestration.
- `lib/features/personalization/screens/privacy_policy/` - Settings legal/privacy subpage with typed mapped policy content.
- `lib/features/personalization/screens/notifications/` - Settings notifications subpage with typed mapped demo notifications and local filtering.
- `lib/features/personalization/screens/help_support/` - Settings Help & Support hub and support option subpages.
- `lib/features/rides/screens/trips/` - Trips tab for ongoing, scheduled, canceled, and completed ride lists plus ride details.
- `lib/navigation_menu.dart` - authenticated app shell that renders passenger or driver tabs based on local app mode.
- `lib/utils/` - constants, helpers, validation, HTTP, storage, logging, device utilities, and theme.
- `context/feature-specs/` - reconstructed prompts/specs that explain how current feature code should be produced.
- `plans/` - ordered implementation plans and decision history.
- Platform folders (`android/`, `ios/`, `web/`, `linux/`, `macos/`, `windows/`) - Flutter platform scaffolding and generated plugin registration.
- Firebase generated config files are local-only and ignored: `lib/firebase_options.dart`, `android/app/google-services.json`, and Apple `GoogleService-Info.plist` files.

## Auth And Access Model

- `AuthGateScreen` decides whether to show auth flow, permissions, or the authenticated navigation shell based on token presence and current user lookup.
- `SAuthRepository` owns real auth API calls through `SHttpClient`; authentication mocks are not used for phone OTP, registration, refresh, logout, or `/me`.
- `STokenStorage` owns secure access and refresh token persistence.
- `SUserStorage` owns non-authoritative cached `/me` user profile data for UI display, including email, gender, and date of birth.
- `SAppModeController` owns local passenger/driver UI mode; auth `role` only gates whether driver mode can be selected.
- Phone OTP verification branches on backend `next_step`: existing phone users receive tokens and enter post-auth routing, while new phone users receive `registration_token` and continue to profile completion with name, email, gender, and DOB.
- Google auth verifies a Google ID token. If the backend requires phone linking, the client routes to `GoogleOtpProfileScreen`, then verifies OTP through `OtpScreen` with `SAuthOtpFlow.googlePhoneLink` and `purpose=phone_link`.
- Permissions are tracked locally using `SPermissionsController` and `SLocalStorage`.
- After permissions are complete, all auth success paths enter `NavigationMenu`; `HomeScreen` is not used as a direct auth destination.
- Approved driver-capable users (`driver` and `admin` roles) can switch the authenticated shell between passenger and driver mode from Settings.
- Docker/local auth testing uses the real Auth service. During local development the backend can print OTPs through `AUTH_OTP_DELIVERY_MODE=console`, while WhatsApp remains the non-console provider.
- Physical-device testing must point `SAFARPAY_AUTH_BASE_URL` at the laptop Wi-Fi IP, not localhost, for example `http://192.168.100.3:8001/api/v1/auth`.
- Passenger map flows call backend Location and Geospatial services for geocoding, reverse geocoding, pickup validation, route preview, and live ride location reads.
- Passenger booking creates backend Ride requests with `HYBRID` pricing for offer-style flows and keeps `FIXED` support available for direct-price flows; passenger UI must not expose `BID_BASED`.
- Temporary passenger ride/location demo mode is active while backend services are unavailable. Location, Geospatial, Ride, Bidding, and live socket repositories return demo fixtures directly, with real HTTP/WebSocket blocks commented beside each method for restoration.
- Active ride tracking uses separate WebSockets for Location live coordinates, Ride lifecycle updates, and Bidding negotiation updates because each backend service owns a different event contract.
- Driver registration status reads from Verification service `GET /api/v1/verification/me`; CNIC, license, selfie, and vehicle steps POST metadata to Verification endpoints, receive presigned upload URLs, and PUT image bytes directly to those URLs.
- Driver vehicle service reuse must be explicit: if an existing vehicle is attached to a new service, the client asks for confirmation before calling the attach-service endpoint.

## Storage Model

- **Secure token storage**: access token and refresh token only.
- **Local app storage**: completion flags such as permissions status, non-authoritative cached user profile data, and the current passenger/driver app mode.
- **Demo ride data**: typed static records and feature fixtures currently power the ride, bidding, location, geospatial, and live socket flows until backend services are available.
- **Mapbox token**: public client token is supplied through `MAPBOX_ACCESS_TOKEN` at build time and is used only for map rendering.
- **Live GPS**: raw passenger GPS is not persisted locally; live coordinates remain in memory for active flows.
- **Driver KYC images**: selected or captured verification images remain screen-local until uploaded to backend-issued presigned URLs; raw images are not persisted by the client feature.
- **Assets**: logos, onboarding images, home banners, home categories, icons, and fonts are local files declared in `pubspec.yaml`.
- **Firebase generated config**: generated locally with FlutterFire CLI and not committed. Use `FIREBASE_SETUP.md`.
- **Generated/build output**: `.dart_tool/`, `build/`, platform ephemeral folders, and plugin symlinks are not source of truth.

## Invariants

1. Auth screens must not bypass `SAuthRepository` for backend-facing auth behavior.
2. Auth routes should use `SAuthNavigation` unless they are part of `AuthFlowScreen`'s internal `AnimatedSwitcher`.
3. Tokens must only be persisted through `STokenStorage`.
4. Cached user profile data must remain non-authoritative; `/me` stays authoritative for role, active, verification, and onboarding checks.
5. User-facing text belongs in `STexts`.
6. Feature UI should use `SColors`, `SSizes`, app theme classes, and `iconsax` where possible.
7. Generated Flutter platform files should not be manually edited unless the change is required and documented.
8. Empty source folders that must survive Git should contain a `.gitkeep`.
9. Feature changes should update matching feature-spec, plan, progress, and decision docs when they alter behavior.
10. Firebase API keys and platform config files must be generated locally, ignored by Git, and restricted/rotated in Google Cloud/Firebase when exposed.
11. Authenticated users must enter the app through `NavigationMenu`; `HomeScreen` remains a tab, not a terminal auth route.
12. Ride DTOs should mirror backend response contracts and keep backend enum wire values stable.
13. A Dart source file should contain one primary widget class unless a very small private helper is truly inseparable.
14. Reusable widgets must move to `lib/common/widgets`; screen-only widgets stay under the owning screen's `widgets/` folder.
15. Reusable page transitions belong in `lib/common/navigation` instead of feature screens.
16. Reusable shadcn widgets must follow `client/.agents/skills/shadcn-ui-flutter/SKILL.md`.
17. Local-only profile edits must not be treated as backend persistence.
18. Settings privacy/legal copy should be rendered from typed mapped content rather than repeated directly in widgets.
19. Demo notifications are local UI data until backend notification and push delivery are planned.
20. Help & Support option destinations are placeholder subpages until support workflows are planned.
21. Trips ride UI should consume backend-aligned `RideResponse` data and keep editing/backend mutations out of the list-only feature unit.
22. Shared search bar UI must stay presentational; feature-specific search results and data composition remain in feature folders.
23. Client code must not call Mapbox Geocoding, Directions, Matrix, or Search APIs directly; those stay backend-mediated.
24. Passenger location tracking uses foreground location only until a separate background-location plan is approved.
25. Driver registration display vehicle options stay separate from Verification backend `VehicleType` values; submission maps display vehicles into the current backend enum values `moto`, `economy`, `comfort`, and `freight`.
26. The final driver review action must stay controlled by Verification `/me` readiness instead of local form completion flags.
27. Feature screens use one screen folder per screen, with one main screen file, screen-local widgets in `widgets/`, and owned subscreens in `screens/`.
28. Map-first passenger booking keeps map rendering common, while booking state, category catalog, and vehicle/fare composition stay feature-owned under Location.
29. Ride lifecycle WebSockets, Bidding negotiation WebSockets, and Location live-coordinate WebSockets must remain separate repositories.
30. Auth `role` must not be treated as the active UI mode; local app mode is a separate preference and must reset to passenger when logout clears auth state.
31. Authentication repositories must not return mock users, mock tokens, or dummy verification tokens; local OTP testing belongs in the backend console provider.
32. OTP verify routing must trust backend `next_step`: `login` persists tokens, `complete_profile` opens profile completion with `registration_token`, and `link_phone` continues Google phone linking.
33. Profile phone number is immutable from the Profile screen; editable profile fields are name, email, gender, and date of birth through Auth `PATCH /me`.
34. Vehicle verification belongs to the physical vehicle; adding that vehicle to another driver service requires explicit user consent in the client before creating the service capability.
