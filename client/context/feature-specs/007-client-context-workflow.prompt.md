# Prompt: Client Context Workflow

Build the client documentation workflow.

## Prompt

Create a documentation system inside `client/` that records what the Flutter app is, how it is structured, what UI and code rules apply, what has been built, what prompts led to the code, what plans were used, and what decisions matter. Add `client/AGENTS.md`, six core context files, a `context/feature-specs` folder for reconstructed prompts, and a `plans` folder for feature-first plans plus operational history.

## Target Files

- `client/AGENTS.md`
- `client/context/project-overview.md`
- `client/context/architecture.md`
- `client/context/ui-context.md`
- `client/context/code-standards.md`
- `client/context/ai-workflow-rules.md`
- `client/context/progress-tracker.md`
- `client/context/feature-specs/**`
- `client/plans/**`

## Acceptance Criteria

- Future agents have a clear read order.
- Feature prompts and plans are ordered before Git-operation plans.
- Progress and decisions identify current auth UI/mock completion and backend integration gaps.
- Docs-only changes do not touch Dart code or generated platform files.

## Status

- Implemented as documentation work.
