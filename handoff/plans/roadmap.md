# NeuroCLI Roadmap

> FUTURE OPTIONS ONLY: This roadmap is not active work, a schedule, or authorization to begin implementation. Current work is defined exclusively in `handoff/active_gate/README.md`.

## Product Direction

NeuroCLI is a terminal-first AI development environment. The Textual app is the flagship surface. React is a supported companion surface over the same backend capability engine. The backend contract matters, but a phase is not product-complete until the docs say what a user can actually do in the application.

The product loop to strengthen is: understand repo state, select target and context, generate a structured proposal, review a diff, validate the result, apply with backup, and prepare a commit with human approval.

## Compound Checkpoint Rule

A compound checkpoint is the required plain-language outcome for every phase and implementation slice: what can a user do after this work that they could not do before?

Each checkpoint must identify where the capability exists: Textual app, React app, API, or backend only. Because Textual is the flagship app, backend-only or React-only work must document the missing Textual checkpoint instead of implying the product capability is complete.

Each phase must carry four statements: the practical user outcome, the backend/API contract, the Textual app outcome, and the React app outcome. If one surface is intentionally deferred, the phase must say so directly.

## Phase 0: Baseline And Documentation

Goal: make the next implementation slice safe to start.

Compound checkpoint: after this phase, a new agent can open the docs and know the active plan, the current product checkpoint, the exact next implementation slice, and which app surfaces must change.

Work: keep active docs current, archive superseded docs, validate Agent Council outputs, document smoke-test commands for Textual, FastAPI, and React, and keep compound checkpoints current.

Exit criteria: the active gate links the required roadmap and contracts, older plans are clearly archived, and council folders validate.

## Phase 1: Shared Proposal And Diff Artifact

Goal: close the generated-file review parity gap and create the first durable AI-edit artifact.

Compound checkpoint: after this phase, React can review backend-generated file proposals instead of treating raw model text as directly applyable file content. Textual already had a local review/apply path, so the shared artifact mostly prevents React from being unsafe or inconsistent.

Backend/API contract: `neurocli_core` creates a generated-file proposal with target path, original content or reference, proposed content, normalized content, diff text, status, and errors. `api` serializes the same artifact on workflow responses.

Textual outcome: no visible app change was required for this phase because Textual already had review, editable draft, diff, backup, and explicit apply behavior. Any future Textual migration to the shared proposal artifact must preserve those behaviors.

React outcome: React can consume `response.proposal`, display the backend diff/proposal status, stage the normalized proposal for review, and keep apply disabled when the proposal is missing or not ready.

Exit criteria: proposal/diff tests pass, API tests cover response shape and workspace path safety, React consumes backend proposal data, and `shared_decisions.md` documents the contract.

## Phase 2: Validation Result Artifact And Safe Validation

Goal: connect generated changes to deterministic verification without unsafe command execution.

Compound checkpoint: after this phase is product-complete, a user should be able to run an approved validation action from the Textual flagship app and see whether it passed, failed, timed out, was skipped, or was rejected by policy. React should show the same validation state once its companion UI is wired.

Backend/API contract: `neurocli_core` defines `ValidationResult`, `ValidationCommand`, `ValidationCommandPolicy`, and a shell-free command runner selected only by approved `command_label`. `api` exposes validation through `POST /api/validate` and workflow responses may include `validation_result`.

Textual outcome: Textual has a Validate action and Ctrl+T path that runs the approved workspace `python_unittest` label or a generated `python_unittest_target` entry for a selected Python file, then displays the shared result artifact.

React outcome: React has a Validate action that calls `/api/validate` with the approved `python_unittest` label and optional selected target, then displays the shared result artifact. React must never accept raw command text as a validation command.

Current implementation status: Phase 2 is complete at the compound-checkpoint level. Both app surfaces can run approved validation and neither accepts arbitrary shell command text.

Exit criteria: command policy is documented, tests cover pass, fail, timeout, skipped, truncation, and policy rejection, Textual exposes the approved validation result in-app, React does not invent unsafe command execution, and both surfaces use the same backend artifact.

## Phase 3: Workflow Timeline

Goal: make AI workflow state visible and inspectable.

Compound checkpoint: after this phase, a user can see where a workflow is in the loop: context collected, target read, model request started, stream complete, proposal created, diff generated, validation run, apply ready, backup created, and commit prepared.

Backend/API contract: `neurocli_core` emits structured timeline events with redaction rules. `api` streams or returns the same event semantics without storing full source or secrets by default.

Textual outcome: Textual shows a concise workflow timeline or activity lane for the current run, with validation and apply readiness visible.

React outcome: React can receive the same timeline events and display them once presentation work starts, without inventing its own workflow states.

Current implementation status: Phase 3 is complete at the compound-checkpoint level. `WorkflowTimelineEvent` lives in `neurocli_core.workflow_timeline`, workflow responses include `timeline`, stream events may include `timeline_event`, API validation/apply/commit responses attach redacted timeline events while preserving existing primary fields, Textual shows the current safe-loop timeline lane, and React consumes the same event shape in a compact status label.

Exit criteria: event ordering is tested for success and error paths, redaction is documented, Textual displays useful state, and React receives the same event shape through the API.

## Phase 4: Terminal-First Experience

Goal: make Textual feel like the flagship developer cockpit without casually changing backend behavior.

Compound checkpoint: after this phase, a user can stay in the Textual app for the full safe loop: choose context, run the model, review a proposal, validate it, edit the draft, apply with backup, inspect radar, and prepare a commit.

Backend/API contract: new behavior remains in `neurocli_core` where practical. Textual uses thin app-side integration over shared services.

Textual outcome: improved command palette, focus order, diff readability, review lane, validation readiness, and safe workflow controls.

React outcome: no React-only behavior is introduced here unless it consumes an already documented backend contract.

Exit criteria: Textual smoke testing covers target, context, model settings, stream, proposal review, validation readiness, apply with backup, radar, and git readiness. No automatic apply or commit happens without explicit user approval.

## Phase 5: Shared Intelligence And React Parity

Goal: bring safety-critical shared capabilities to React through real backend contracts.

Compound checkpoint: after this phase, a React user can perform the same safety-critical review loop available in Textual where the backend supports it, while any remaining parity gaps are explicitly documented.

Backend/API contract: proposal, validation, timeline, radar, and git-readiness contracts remain backend-defined. React consumes them through `api`.

Textual outcome: Textual remains the reference implementation for the terminal-first loop.

React outcome: React presents proposal/diff artifacts, validation results, workflow timeline state, radar intelligence, and git readiness without duplicating backend logic.

Exit criteria: React does not invent backend behavior, React build and browser smoke checks pass, parity exceptions are documented, and both frontends expose equivalent safety guarantees for shared workflows.

## Phase 6: State-Of-The-Art Layer

Goal: add advanced capabilities only after the core loop is reliable.

Compound checkpoint: after this phase, users can use advanced capabilities such as model profiles, local evals, traces, connectors, background lanes, or planning sessions through explicit permission gates and reviewed artifacts rather than autonomous hidden behavior.

Backend/API contract: advanced features are built from durable artifacts, permission gates, redaction rules, and human approval.

Textual outcome: advanced controls appear first where they strengthen the terminal-first workflow.

React outcome: React receives advanced surfaces only after Codex defines the backend/API contract and safety model.

Exit criteria: eval fixtures run locally without live model credentials by default, traces redact sensitive content, connector design includes permission and audit rules, and planning sessions create reviewed artifacts rather than autonomous code changes.

## Non-Goals For Phase 4

Do not start model profiles, MCP-style connectors, background task lanes, autonomous commits, productized council UI, or React-only orchestration controls during the terminal-first experience slice unless the active plan explicitly changes.
