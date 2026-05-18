# Driver Verification Demo Status Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let the driver registration checklist render all Verification `/me` states without a running backend.

**Architecture:** Keep the screen and controller unchanged as consumers of `SDriverVerificationRepository`. Add backend-shaped demo fixtures behind the repository and preserve the real HTTP call as the documented restore path.

**Tech Stack:** Flutter, Dart, GetX, existing driver registration models, and Flutter tests.

---

## Tasks

- [ ] Create `driver_verification_demo_data.dart` with a demo scenario enum and an active scenario constant.
- [ ] Add backend-shaped demo responses for not-started, partial, ready-to-submit, under-review, verified, single rejected groups, and multiple rejected groups.
- [ ] Update `SDriverVerificationRepository.getMyVerificationStatus()` to return the active demo response.
- [ ] Keep the real `SHttpClient.get('/me')` code commented with explicit restore instructions.
- [ ] Add tests that parse every demo scenario.
- [ ] Add tests for under-review blocked cards, verified approved blocked cards, and rejection reason exposure.
- [ ] Update client feature-spec, plan, progress tracker, and decisions log.
- [ ] Run `flutter analyze` and `flutter test`.

## Acceptance Criteria

- Changing `activeDriverVerificationDemoScenario` changes the checklist UI state.
- No backend is required to render the verification status screen.
- Demo data preserves the real backend `/me` wire shape.
- The real backend call can be restored from the repository comment.
- Analyzer and tests pass.

## Restore Notes

This is temporary UI verification scaffolding. Before production backend integration, restore the repository HTTP call and remove or disable the demo return.
