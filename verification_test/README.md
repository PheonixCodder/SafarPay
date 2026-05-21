# Verification Local Review Harness

This folder lets you test the verification review pipeline with local files before using real app uploads.

It exercises the same service-level flow used by `POST /submit-review`:

1. Seed a driver.
2. Seed an active vehicle.
3. Seed all required driver and vehicle document rows.
4. Call `VerificationUseCases.request_verification_review(user_id)`.
5. Call `VerificationUseCases.execute_verification_review(driver_id)`.
6. Print final statuses, extracted OCR metadata, published events, and rejection reasons.

## Required Assets

Put these files in `verification_test/assets/`:

- `id_front.png`
- `id_back.png`
- `license_front.png`
- `license_back.png`
- `selfie_id.png`
- `registration_doc_front.png`
- `registration_doc_back.png`
- `vehicle_photo_front.png`
- `vehicle_photo_back.png`

The exact extension can be changed in `sample_case.json`; the runner follows the paths in that JSON file.

The current ML engine processes only:

- `id_front.png`
- `id_back.png`
- `license_front.png`
- `license_back.png`
- `selfie_id.png`

The vehicle files are still required because `/submit-review` validates them and marks them verified/rejected with the rest of the review.

Pakistan document rules represented by the fixture:

- `id_front` carries the CNIC expiry date.
- `id_back` has no expiry date.
- Physical license: use separate `license_front` and `license_back` files.
- E-license: point both `license_front.path` and `license_back.path` to the same front image file.
- `registration_doc_front` and `registration_doc_back` have no expiry dates.

## Run Inside The Verification Container

Recommended, because the container already has TensorFlow, DeepFace, PaddleOCR, OpenCV, and native Linux libs:

```powershell
docker compose run --rm --no-deps -v "C:\Users\ubaid\OneDrive\Desktop\SafarPay\verification_test:/app/verification_test" verification python verification_test/run_local_review.py --case verification_test/sample_case.json
```

To check that the referenced files exist before running the ML pipeline:

```powershell
docker compose run --rm --no-deps -v "C:\Users\ubaid\OneDrive\Desktop\SafarPay\verification_test:/app/verification_test" verification python verification_test/run_local_review.py --case verification_test/sample_case.json --validate-only
```

## Run Locally

Local execution requires the verification service dependencies installed for Python 3.10:

```powershell
$env:UV_CACHE_DIR=".uv-cache"
uv run --package verification python verification_test/run_local_review.py --case verification_test/sample_case.json
```

## Testing Correct And Incorrect Docs

Yes, this is the right way to analyze production behavior:

- Use one case with correct matching CNIC, license, and selfie.
- Use one case with a mismatched selfie.
- Use one case with expired CNIC/license dates.
- Use one case with wrong or noisy OCR text in `metadata_json.ocr_text`.
- Use one case with missing vehicle docs to confirm `/submit-review` rejects early.

For OCR-focused tests, you can put cached OCR text in `sample_case.json` under:

- `documents.id_front.metadata_json.ocr_text`
- `documents.license_front.metadata_json.ocr_text`

If `ocr_text` exists, the engine uses it instead of running OCR for that document.
