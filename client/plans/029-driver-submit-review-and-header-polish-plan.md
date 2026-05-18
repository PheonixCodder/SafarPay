# Driver Submit Review And Header Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a submit-review CTA when all driver verification sections are ready and improve the verification status header layout.

**Architecture:** Keep status rendering in `DriverVerificationStatusScreen`, eligibility and submit state in `SDriverVerificationController`, and API/demo behavior in `SDriverVerificationRepository`.

**Tech Stack:** Flutter, Dart, GetX, existing SafarPay constants/widgets, and Flutter tests.

---

## Tasks

- [ ] Add `SReviewSubmissionResponse` for `POST /submit-review`.
- [ ] Add `SDriverVerificationRepository.submitForReview()` with demo response and commented production HTTP call.
- [ ] Add `isSubmittingReview`, `canSubmitForReview`, and `submitForReview()` to `SDriverVerificationController`.
- [ ] Render an `ElevatedButton` beneath the four verification cards only when all four groups are pending.
- [ ] Update demo default to `readyToSubmit` so the CTA is immediately visible while backend is unavailable.
- [ ] Improve the `SPrimaryHeaderContainer` content with a stacked text/image composition.
- [ ] Add centralized strings for header subtitle and submit button states.
- [ ] Add tests for submit eligibility, blocked scenarios, and demo submit transition to under-review.
- [ ] Update feature-spec, progress tracker, UI context, and decisions log.
- [ ] Run `flutter analyze --no-pub` and `flutter test`.

## Acceptance Criteria

- Ready-to-submit state shows a `Submit for Review` button beneath the checklist.
- Non-ready states do not show the button.
- Pressing the button in demo mode moves the status to under-review.
- Header text and image no longer collide or look misaligned.
- Existing driver registration cards and skeleton screen navigation remain unchanged.
- Analyzer and tests pass.

## Restore Notes

When the backend is available, restore the repository HTTP call to `POST /submit-review` and reload `/me` after success instead of forcing the local demo under-review response.
