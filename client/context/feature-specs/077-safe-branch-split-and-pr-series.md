# Safe Branch Split And PR Series (077)

## Prompt

Analyze the entire dirty repository state, split the current work into professional feature branches, push each branch, open a PR, merge it, and then continue to the next branch without losing or corrupting any code.

## Requirements

- Preserve the full current workspace before splitting.
- Group changes by coherent feature boundaries instead of one giant PR.
- Commit only the files that belong to each branch.
- Push branches to GitHub, open PRs, merge them, and proceed sequentially.
- Keep all local-only or unmergeable artifacts safe.
- Avoid destructive git operations unless every path is backed up and verified.

## Proposed Branch Groups

1. **SP Platform Infrastructure (`feature/077-sp-platform-infra`)**:
   - Platform core config, messaging contracts, kafka utilities.
   - Tests and docker configurations.

2. **Notification Service & Migrations (`feature/077-notification-service`)**:
   - Notification service backend logic, dependencies, database migrations, and push clients.
   - Associated backend tests.

3. **Backend Core Services & Tests (`feature/077-backend-services-core`)**:
   - Bidding, Geospatial, Ride, Verification, Payment, and Communication services.
   - Associated use cases, infrastructure, database models, and unit/integration tests.

4. **Flutter Client Notifications (`feature/077-client-notifications`)**:
   - Notification inbox model, screen, widgets, and popup.
   - Category asset images and API/image constants.
   - Firebase messaging Android native service integrations.

5. **Flutter Client Ride Orchestration & Active Ride (`feature/077-client-ride-orchestration`)**:
   - Navigation recovery, trips controller, pending ride matching, active ride foreground/overlay services.
   - Ride stepper tile, switch tile, fuel chips, and relevant client tests.

6. **Feature Specs and Plans (`feature/077-specs-and-plans`)**:
   - Client feature specs (063 to 077).
   - Client plans (063 to 077).

## Safety Notes

- Full state must be preserved under a backup branch before any hard resets.
- Git configuration must use non-interactive credential setup via GitHub CLI.
