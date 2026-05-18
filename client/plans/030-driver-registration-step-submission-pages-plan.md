# Driver Registration Step Submission Pages Plan

## Summary

Build real CNIC, license, selfie, and vehicle submission pages behind the existing Verification status checklist. Each page validates local form data, asks the Verification service for presigned document upload URLs, uploads selected image bytes, and returns to the status screen so `/me` can be refreshed.

## Implementation

- Add `image_picker` for document/vehicle image selection and `camera` for selfie-with-license realtime capture.
- Add camera/photo platform permission declarations for Android and iOS.
- Extend driver registration models with presigned URL response models, submission request serializers, and a backend verification vehicle enum mapping.
- Extend `SDriverVerificationRepository` with `submitCnic`, `submitLicense`, `submitSelfie`, `submitVehicle`, and presigned PUT upload support while retaining backend-offline demo responses.
- Add validators for CNIC, license number, future expiry date, bounded integers, and vehicle fields.
- Add a reusable `SImageUploadTile` for document/photo upload slots.
- Create one controller per step page to own form controllers, selected images, validation, loading, errors, and submission.
- Replace the old skeleton step screens with folder-based real pages and update `verification_status_screen.dart` to await page results and refresh status.
- Keep final review submission controlled by the status screen and `/me` readiness only.

## Test Plan

- Add unit tests for request JSON serialization, presigned response parsing, and vehicle type mapping.
- Run `flutter test`.
- Run `flutter analyze --no-pub`.
- Run Dart formatting on touched Dart files.

## Decisions

- The client sends Verification backend enum values (`moto`, `economy`, `comfort`, `freight`) even though display vehicle labels remain richer.
- The selfie page uses the camera plugin instead of gallery upload to keep the authenticity flow strict.
- Demo mode remains at the repository boundary until the verification backend can be run locally.
