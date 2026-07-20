# Frontend Parity And Differences

## Purpose

NeuroCLI has two product surfaces: the Textual app and the React web app. They share backend behavior through `neurocli_core`, but they do not have to expose identical features at the same time.

This file documents intentional differences so agents do not treat every mismatch as a bug or accidentally erase useful surface-specific behavior.

## Product Roles

Textual is the flagship app. It should usually receive core workflow capabilities first when those capabilities are part of the terminal-first developer loop.

React is the companion web app. It can have browser-specific presentation, file browsing, layout, and review affordances when those are useful, as long as it does not duplicate backend business logic or invent unsafe backend behavior.

The rule is not "both apps must be identical." The rule is: shared safety-critical behavior must come from the same backend contract, and intentional differences must be documented here.

## Current Capability Matrix

| Capability | Textual app | React app | Status |
| --- | --- | --- | --- |
| Prompt execution | Available through shared workflow adapter | Available through FastAPI bridge | Shared backend behavior |
| Streaming AI responses | Available through `stream_ai_workflow` | Available through `POST /api/ai/stream` | Shared event semantics |
| Target file selection | Available through Textual controls | Available through file tree and target browse modal | Surface-specific UI |
| Context file selection | Available through Textual context flow | Available through file tree paperclip and context modal | Shared request fields, different UI |
| Model and options | Available through Textual model modal | Available through React model modal | Shared request fields |
| Generated-file review | Available through existing Textual review/apply path | Available through backend `response.proposal` artifact | Different implementation paths, shared safety goal |
| Editable review draft | Available | Available | Surface-specific editors |
| Apply with backup | Available locally through Textual path | Available through `/api/apply` | Shared safety behavior, different call path |
| Formatting existing files | Available locally through core formatter/diff | Available through `/api/format` | Same backend services, different call path |
| Radar/workspace health | Available locally through core radar services | Available through `/api/radar` | Same backend services |
| Git status/diff/commit | Available with Textual git modal and AI commit message helper | Available through manual Git modal over API status/diff/commit | Intentional difference |
| AI commit message generation | Available in Textual | Not exposed in React | Intentional until Codex defines a shared API contract |
| Validation result artifact | Available in status strip and validation output | Available in status strip and validation output | Shared backend artifact |
| Running approved validation from UI | Available through Validate / Ctrl+T using `python_unittest` | Available through Validate using `python_unittest` | Shared safe label, different UI |
| Workflow timeline | Available as a visible Textual safe-loop lane | Consumed from API and shown as compact status | Shared backend artifact, different presentation depth |

## Intentional Differences

Textual may have terminal-first controls that React does not need, such as keyboard bindings, command palette behavior, compact terminal status, and direct local workflow integrations.

React may have browser-native affordances that Textual does not need, such as richer file tree browsing, modal layouts, responsive panels, or companion dashboard-style presentation.

Git behavior is intentionally different right now. Textual can generate AI commit messages through `neurocli_core.git_engine`; React only exposes manual commit status, diff, and commit operations through the API. Do not add AI commit messages to React until Codex defines a shared contract.

Generated-file review is intentionally not identical internally. Textual keeps its existing review/apply path because it already protects editable review, diff, backup, and explicit apply. React consumes the shared proposal artifact so it does not apply raw model output.

Validation is now aligned at the Phase 2 level. Both apps can run the approved `python_unittest` validation label and display the shared result artifact. Neither app accepts raw command text.

Workflow timeline is aligned at the backend contract level and intentionally different in presentation. Textual is the flagship surface and shows a visible safe-loop lane for the current run. React consumes the same `timeline` and `timeline_event` payloads through the API but currently displays a compact companion status label so Gemini can later improve presentation without inventing frontend-only workflow states.

## Documentation Rule

When one surface gets a feature the other does not have, update this file in the same implementation slice.

Each entry should say whether the difference is temporary, intentional, or a blocked parity gap. If a feature is safety-critical, document the backend contract that prevents the two apps from drifting into different behavior.

If React can do something Textual cannot do, that is allowed. It must be documented here with a short explanation of why the difference is acceptable and whether Textual should catch up later.

If Textual can do something React cannot do, that is also allowed. It must be documented here so Gemini does not accidentally build frontend-only logic to imitate backend behavior without a contract.
