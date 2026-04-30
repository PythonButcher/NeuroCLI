# Phase 5 Direction

## Purpose

Phase 5 should make NeuroCLI feel like a serious terminal-first developer tool while keeping the architecture disciplined. The product now has one shared Python backend workflow in `neurocli_core` and two supported frontends: the full Textual app in `neurocli_app`, and the React frontend in `web_client` through the FastAPI bridge in `api`.

The goal is not to make two unrelated products. The goal is to make both frontends feel intentional, fast, and feature-complete while preserving one backend contract.

## Product Principle

NeuroCLI should still feel like a terminal application. The Textual version should be the flagship terminal experience, with dense keyboard-first workflows, live streaming, file-aware review, and clear state. The React version should echo the same workflow model for users who prefer a browser surface, but it should not invent separate backend behavior.

When the two frontends differ, the difference should be presentation-driven. Prompt execution, file updates, context attachments, model selection, formatting, apply behavior, radar, and git actions should stay aligned where the backend supports them.

## Phase 5 Outcomes

The main outcome is a polished, coherent frontend layer for both app surfaces. A user should understand what file is targeted, what context is attached, what model settings are active, what the AI is doing during streaming, what changed after generation, and what action will be taken when applying or committing.

The second outcome is feature parity. If the Textual app can target a file, stream a response, attach context, format, apply, inspect radar, and use git actions, the React frontend should expose the same behavior unless there is a documented reason not to.

The third outcome is stronger local reliability. Startup instructions, dependency setup, local URLs, environment variables, and smoke-test steps should be clear enough that a future agent can verify both frontends without rediscovering the project layout.

## Terminal-First Ideas

NeuroCLI can stand out by making the terminal feel like a real cockpit instead of a chat box. The Textual app should have a strong command-center layout: workspace tree, active target file, context stack, model state, streaming output, proposed diff, and action rail all visible without feeling crowded.

The strongest interaction upgrade would be a command palette. It should let a user jump to files, attach context, switch model profiles, run format, open radar, view git status, apply changes, and rerun the last prompt without reaching for the mouse. This fits the terminal identity and can also map well to React later.

The app should make AI state visible. During a run, show whether NeuroCLI is reading target content, adding context, streaming model output, formatting generated code, creating a diff, or waiting for apply. This should be status-driven from the workflow layer where possible, not hardcoded decoration.

The file-targeted workflow can become the signature feature. A user should be able to select a file, ask for a change, see a streaming full-file proposal, review a clean diff, apply with backup, and inspect the result without losing context. That is the core loop to polish first.

Radar can become more than a modal. It could evolve into a workspace intelligence panel: recent AI edits, technical debt hotspots, large files, risky uncommitted changes, stale generated backups, and files with repeated failed formatting. That gives NeuroCLI a reason to feel native to the repo instead of being a generic prompt window.

Git can become a review lane. Before commit, show changed files, staged versus unstaged state, generated commit message, risk notes, and a final confirmation. Keep the backend in `neurocli_core.git_engine`, but make the frontends present the same commit story clearly.

## Feature Parity Checklist

Both frontends should support prompt runs, streaming output, file-targeted updates, context attachments, model override, model options, formatting, diff review, apply with backup, radar, git status, git diff, and commit flow.

The Textual app should also prioritize keyboard navigation, focus order, terminal-safe colors, compact layout, and fast state changes. The React app should prioritize browser reliability, responsive layout, accessible controls, and clear backend error handling.

## Design Direction

The visual language should be terminal-native but not plain. Use strong contrast, restrained color, compact typography, visible keyboard focus, and meaningful status regions. Avoid a generic chat interface. NeuroCLI should feel like a developer instrument panel wrapped around the repo.

For the Textual app, the strongest direction is a split workspace with a file/context rail, a central stream and diff area, and a lower command dock. Use color to encode state: target selected, context attached, model overridden, changes proposed, apply ready, git dirty, and error.

For the React app, the strongest direction is to mirror the same mental model without copying every terminal constraint. It should feel like a web version of the terminal workflow: dense, inspectable, keyboard-friendly, and built around files and diffs rather than marketing-style panels.

## Phase 5 Guardrails

Do not add frontend-only business rules. If a new feature needs workflow data, add or extend it in `neurocli_core` first, then expose it through `api` for React and directly through the Textual app.

Do not let the React app become the better-supported product at the expense of the Textual app. The terminal version is still a first-class surface.

Do not polish UI around broken flows. Before visual refinement, each major action should have a known backend path, a loading state, an error state, and a recovery path.

## Suggested Phase 5 Order

Start with a parity audit. Compare the Textual app and React frontend feature by feature and document gaps in `handoff/coordination/shared_decisions.md`.

Next, stabilize the shared user flows: prompt, target file, context, model settings, stream, diff, apply, radar, and git.

Then polish the Textual app as the flagship terminal experience. Improve layout, keyboard flow, active state visibility, streaming status, diff review, and action discoverability.

After that, polish the React app to match the same behavior and mental model. Gemini can own visual presentation in `web_client`, while Codex owns any state, API, or backend contract changes.

Finish with smoke tests and updated run docs so Phase 6 can expand automated end-to-end coverage instead of cleaning up ambiguity.
