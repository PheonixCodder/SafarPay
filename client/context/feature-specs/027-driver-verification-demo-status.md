# 027 Driver Verification Demo Status

Add a temporary backend-offline demo mode for the driver registration verification checklist.

## Goal

The Verification backend may be unavailable during UI work. The client should still render every checklist state using backend-shaped demo data, without changing the screen UI path.

## Behavior

- `DriverVerificationStatusScreen` continues to read state through `SDriverVerificationController`.
- `SDriverVerificationController` continues to read state through `SDriverVerificationRepository`.
- `SDriverVerificationRepository.getMyVerificationStatus()` temporarily returns a selected demo `/me` response instead of calling the backend.
- The real HTTP call remains commented in the repository with restore instructions.
- Demo scenarios are switched by changing one enum constant in the demo data file.

## Demo Scenarios

Required scenarios:

- `notStarted`
- `partiallySubmitted`
- `readyToSubmit`
- `underReview`
- `verified`
- `identityRejected`
- `licenseRejected`
- `selfieRejected`
- `vehicleRejected`
- `multipleRejected`

Every scenario must use the same JSON shape as Verification service `GET /api/v1/verification/me`:

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

## Restore Path

When the backend is available again, remove the demo return from `SDriverVerificationRepository.getMyVerificationStatus()` and restore the commented `SHttpClient.get('/me', service: SApiService.verification, requiresAuth: true)` call.
