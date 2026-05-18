# 028 Driver Submit Review And Header Polish

Add the final checklist action for driver verification review and improve the driver registration status header layout.

## Goal

When all four Verification `/me` groups are submitted, the driver registration checklist should show a `Submit for Review` button beneath the four checklist cards. The action should call the Verification submit-review route when backend mode is active, and simulate the same result in local demo mode.

The status header should also look more polished: category and vehicle text should be readable and intentionally placed, while the driver/car image should sit lower and right-aligned without crowding the text.

## Submit Review Behavior

- Show `Submit for Review` only when:
  - `overall_status == pending`
  - `identity.status == pending`
  - `license.status == pending`
  - `selfie.status == pending`
  - `vehicle.status == pending`
- Hide the button for not-started, partially submitted, under-review, verified, and rejected states.
- On tap:
  - call `SDriverVerificationRepository.submitForReview()`
  - show `Submitting...` while the call is in flight
  - after success, move the UI to the under-review state in demo mode
  - when backend mode is restored, reload `/me` after submit-review succeeds

Backend route:

```text
POST /api/v1/verification/submit-review
```

Expected response:

```json
{
  "status": "UNDER_REVIEW",
  "estimated_time_seconds": 30
}
```

## Header Behavior

- Keep using `SPrimaryHeaderContainer`.
- Keep `SAppBar` at the top.
- Replace the current simple row with a stacked header composition:
  - vehicle label in a small light chip
  - category title below the chip
  - short helper subtitle below the title
  - driver/car image positioned lower and to the right
- Use `SColors`, `SSizes`, `SOpacities`, and theme text styles.
- Avoid overlap on small screens by giving the text and image their own constrained areas.

## Demo Mode

Set `activeDriverVerificationDemoScenario` to `readyToSubmit` to verify the button immediately. Other scenarios remain available for visual QA.
