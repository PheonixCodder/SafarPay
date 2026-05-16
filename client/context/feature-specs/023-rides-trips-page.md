# Prompt: Rides Trips Page

Create a professional Trips page for SafarPay ride history and active ride tracking.

## Goal

Replace the Trips bottom-navigation placeholder with `client/lib/features/rides/screens/trips/trips.dart`. The page must use `SAppBar`, no `SPrimaryHeaderContainer`, and four top tabs for Ongoing, Scheduled, Canceled, and Completed rides.

## Requirements

- Read `client/AGENTS.md` and context files before editing.
- Use the existing `SNavigationBar` animated indicator approach as the pattern for the Trips tab control.
- Add tab labels and ride labels to `STexts`.
- Use demo rides from `client/lib/data/rides/demi_rides.dart`.
- Keep `RideResponse` backend-aligned with the ride service response model.
- Add or adjust demo ride data so all four tabs have representative records.
- Filter tabs as:
  - Ongoing: `CREATED`, `MATCHING`, `ACCEPTED`, `ARRIVING`, `IN_PROGRESS` and not scheduled.
  - Scheduled: `isScheduled == true` and not completed/canceled.
  - Canceled: `CANCELLED`.
  - Completed: `COMPLETED`.
- Create distinct ride cards per state through shared card configuration, not duplicated layouts.
- Add a common `View details` button used by all cards.
- Open `client/lib/features/rides/screens/trips/screens/ride/ride.dart` for ride details.
- Show core ride data: route, status, service type, category, pricing mode, price, payment method, schedule/completion/cancel timestamps, cancellation reason, stops, proof count, and verification count.
- Keep one primary widget per file and use widgets under each existing `widgets/` folder where appropriate.
- Use `SColors`, `SSizes`, `STexts`, `SRightSlidePageRoute`, and existing common components.
- Avoid boxy dashboard-card design; use a compact operational timeline/list style.
- Update context docs, the saved implementation plan, progress, and decision log.

## Acceptance Criteria

1. Bottom navigation Trips tab opens `TripsScreen`.
2. Four top tabs switch with a smooth animated segmented indicator.
3. Each tab shows only its intended ride statuses.
4. Every tab card has a shared `View details` button.
5. The details page opens from every card and shows full ride information.
6. Demo ride data includes scheduled, ongoing, canceled, and completed rides.
7. The design uses SafarPay colors, spacing, typography, and professional non-boxy cards.
