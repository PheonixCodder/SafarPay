# 026 Driver Registration Flow

Build a passenger-account entry point for driver onboarding from Settings. The user taps `Register as a Driver`, chooses how they want to earn, chooses a vehicle option for that earning category, and then lands on a Verification-service-backed registration checklist.

## Entry And Navigation

- Entry point: `client/lib/features/personalization/screens/settings/settings.dart`.
- The settings row titled `Register as a Driver` opens `DriverRegistrationScreen`.
- Navigation uses `SRightSlidePageRoute` from `client/lib/common/navigation/right_slide_page_route.dart`.

## Flow

1. `DriverRegistrationScreen`
   - Title: `How do you want to work with us`.
   - Shows five earning categories in a light-mode list layout:
     - City driver
     - Courier
     - City to City driver
     - Freight driver
     - Grocery delivery
   - Uses the same category assets as the Home categories feature.

2. `DriverVehicleSelectionScreen`
   - Title: `Choose your vehicle`.
   - Shows vehicle options based on selected earning category.
   - Vehicle image constants live in `SImages`; actual missing files may be added later.

3. `DriverVerificationStatusScreen`
   - Uses `SAppBar` and `SPrimaryHeaderContainer`.
   - Header renders `SImages.driverRegistrationHeader`.
   - Calls Verification service `GET /api/v1/verification/me`.
   - Renders four checklist cards:
     - CNIC Info
     - Driver's License
     - Selfie with License
     - Vehicle Info

## Backend Contract

The status screen consumes the backend aggregated response:

```json
{
  "driver_id": "UUID | null",
  "overall_status": "not_started|pending|under_review|verified|rejected",
  "identity": { "status": "not_submitted|pending|verified|rejected", "documents": [], "rejection_reason": null },
  "license": { "status": "not_submitted|pending|verified|rejected", "documents": [], "rejection_reason": null },
  "selfie": { "status": "not_submitted|pending|verified|rejected", "documents": [], "rejection_reason": null },
  "vehicle": { "status": "not_submitted|pending|verified|rejected", "documents": [], "rejection_reason": null }
}
```

The client must not submit documents in this feature unit. The four detail screens are skeletons only. Real CNIC, license, selfie, vehicle form, presigned URL, direct S3 upload, and submit-review behavior are deferred.

## State Rules

- `not_started`: all checklist cards are open and show empty circle state.
- `pending`: submitted groups show submitted/progress state; remaining groups stay open.
- `under_review`: all checklist cards are blocked and the user sees an under-review notice.
- `rejected`: rejected groups show cross icons and rejection reason text when available; correction screens remain reachable for later resubmission work.
- `verified`: all cards show approved status and the user sees an already-registered message for the selected vehicle.

## Vehicle Mapping

Display options:

- City driver: Car, Motorcycle, Rickshaw.
- Courier: Motorcycle, Car, Rickshaw.
- City to City driver: Car, Van.
- Freight driver: Pickup, Mini truck, Truck.
- Grocery delivery: Motorcycle, Car.

Verification backend `VehicleType` is currently narrower (`moto`, `economy`, `comfort`, `freight`), so this feature keeps display choices separate from backend submission values until the detailed vehicle form is implemented.
