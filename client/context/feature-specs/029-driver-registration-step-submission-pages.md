# Driver Registration Step Submission Pages Prompt

Implement the production-shaped driver registration step pages for the SafarPay Flutter client. The user reaches this flow from Settings > Register as a Driver, chooses how they want to work, chooses a vehicle, then lands on `verification_status_screen.dart`.

Each of the four checklist tabs must open a real form page:

- CNIC: `client/lib/features/personalization/screens/driver_registration/screens/cnic`
- License: `client/lib/features/personalization/screens/driver_registration/screens/license`
- Selfie with license: `client/lib/features/personalization/screens/driver_registration/screens/selfie`
- Vehicle info: `client/lib/features/personalization/screens/driver_registration/screens/vechicle_info`

Use `SAppBar` for back navigation. Keep the status screen as the canonical parent; after a step page submits successfully it should return to the status screen and refresh Verification `/me`.

Backend routes come from `services/verification/verification/api/router.py`:

- `POST /driver/cnic`
  - Request: `id_number`, `expiry_date`
  - Response upload keys: `id_front`, `id_back`
- `POST /driver/license`
  - Request: `license_number`, `expiry_date`
  - Response upload keys: `license_front`, `license_back`
- `POST /driver/selfie`
  - Request: empty JSON object
  - Response upload key: `selfie_id`
- `POST /driver/vehicle`
  - Request: `vehicle_id`, `brand`, `model`, `color`, `vehicle_type`, `max_passengers`, `plate_number`, `production_year`
  - Response upload keys: `registration_doc_front`, `registration_doc_back`, `vehicle_photo_front`, `vehicle_photo_back`

The backend returns presigned PUT URLs. The client must first submit the step metadata, then upload each required image to the matching presigned URL. The final `Submit for Review` button remains on the status screen only and appears only when `/me` reports all four groups as `pending` and overall status is `pending`.

Design the pages as professional light-mode mobile forms using SafarPay tokens (`SColors`, `SSizes`, `STexts`) and Iconsax. Document upload fields may use gallery upload or realtime camera capture. The selfie step must use realtime camera capture only and provide retry/use-this-photo confirmation before submission.

Keep one primary widget per Dart file. Add reusable upload components under `client/lib/common/widgets` only when they are generic. Add validation/helpers under `client/lib/utils` when reusable. Keep backend unavailable demo mode working with backend-shaped dummy presigned responses.
