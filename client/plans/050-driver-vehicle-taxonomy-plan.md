# 050 - Driver Vehicle Taxonomy Plan

## Summary

Normalize driver registration and ride matching so service type, vehicle type, category, and pricing mode are separate concepts.

## Implementation

- Replace verification vehicle buckets with canonical seven vehicle types.
- Add verification driver service capabilities for `driver + vehicle + service_type`.
- Align ride vehicle type enums to the same canonical seven values.
- Add a ride repository/use-case guard that rejects assigning or accepting a second active ride for the same driver.
- Require passenger ownership when adding stops to an active ride.
- Update Flutter driver registration to send canonical `vehicle_type` and selected `service_type`.
- Update passenger booking demo/request vehicle strings from old body-style values to canonical vehicle types.

## Validation

- Backend syntax check passes for changed verification, ride, and migration files.
- Focused tests were updated for canonical vehicle contracts and active-driver rejection.
- Full focused pytest execution is blocked in this environment by missing optional packages (`cv2`, `boto3`) in the current uv environment.
