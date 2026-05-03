# NeuroCLI Roadmap

## Product Direction

NeuroCLI should become a terminal-first AI development environment. The Textual app is the flagship surface. React remains a supported companion surface over the same backend capability engine. Structured agent orchestration is a later layer that should grow from durable, validated artifacts rather than from autonomous behavior.

The product loop to strengthen is: understand repo state, select target and context, generate a structured proposal, review a diff, validate the result, apply with backup, and prepare a commit with human approval.

## Phase 0: Baseline And Documentation

Goal: make the next implementation slice safe to start.

Work: keep active docs current, archive superseded docs, validate Agent Council outputs, and document the exact local smoke-test commands for Textual, FastAPI, and React.

Exit criteria: active docs point to this roadmap, older plans are clearly archived, council folders validate, and a new agent can tell what to work on without reading stale phase plans first.

## Phase 1: Shared Proposal And Diff Artifact

Goal: close the most important parity gap and create the first durable AI-edit artifact.

Work: define a shared generated-file proposal artifact in `neurocli_core`. It should capture the target path, original content or original content reference, proposed content, normalized or formatted content when available, diff text, proposal status, and errors. Expose the same artifact through `api` for React. Keep Textual's existing review/apply path intact until migration is proven safe.

Exit criteria: proposal/diff tests pass, API tests cover the response shape and workspace path safety, React can review backend-generated proposal data, and `shared_decisions.md` documents the contract.

## Phase 2: Validation Result Artifact

Goal: connect generated changes to deterministic verification without unsafe command execution.

Work: design a validation-result artifact with status, command label, duration, exit code, skipped state, short output excerpt, and error details. Start with an explicit allowlist or project-configured command set. Do not let model output execute arbitrary shell commands.

Exit criteria: validation command policy is documented, unit tests cover pass, fail, timeout, skipped, and output-truncation states, and both frontends can eventually display validation readiness from the same backend shape.

## Phase 3: Workflow Timeline

Goal: make AI workflow state visible and inspectable.

Work: introduce structured workflow timeline events such as context collected, target read, model request started, stream complete, proposal created, diff generated, validation run, apply ready, backup created, and commit prepared. Keep trace content redacted by default and avoid storing full source or secrets in timeline artifacts.

Exit criteria: timeline event ordering is tested for success and error paths, Textual can show clear workflow state, and React can receive the same event semantics through the API when presentation work begins.

## Phase 4: Terminal-First Experience

Goal: make Textual feel like the flagship developer cockpit without changing backend behavior casually.

Work: add a Textual command palette over existing safe actions, improve focus order, improve diff readability, strengthen the review lane, and make validation readiness visible. Keep all new behavior either in `neurocli_core` or as a thin app-side integration over existing services.

Exit criteria: Textual smoke testing covers target, context, model settings, stream, proposal review, validation readiness, apply with backup, radar, and git readiness. No automatic apply or commit happens without explicit user approval.

## Phase 5: Shared Intelligence And React Parity

Goal: bring shared safety-critical capabilities to React through real backend contracts.

Work: update React to present proposal/diff artifacts, validation results, workflow timeline state, radar intelligence, and git readiness where the backend supports them. Gemini can handle React presentation only after Codex wires the integration and documents the data shape.

Exit criteria: React does not invent backend behavior, React build and browser smoke checks pass, parity exceptions are documented, and both frontends expose equivalent safety guarantees for shared workflows.

## Phase 6: State-Of-The-Art Layer

Goal: add advanced capabilities only after the core loop is reliable.

Work: consider model profiles, local prompt/workflow evals, local traces, MCP-style connector boundaries, background task lanes, and productized planning or council sessions. These should be built from durable artifacts, permission gates, redaction rules, and human approval.

Exit criteria: eval fixtures run locally without live model credentials by default, traces redact sensitive content, connector design includes permission and audit rules, and planning sessions create reviewed artifacts rather than autonomous code changes.

## Non-Goals For The Next Slice

Do not start with MCP connectors, background task lanes, autonomous commits, productized council UI, or React-only diff logic. Those are later capabilities. The next slice is the shared proposal/diff artifact because it closes the current parity gap and creates the foundation for validation, timeline, review, and orchestration.
