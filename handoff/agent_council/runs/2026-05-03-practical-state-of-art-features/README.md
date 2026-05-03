# Practical State-Of-The-Art Features Council Run

This folder contains the Agent Council run for the feature-direction subject:

What practical and state-of-the-art features should NeuroCLI consider adding, while preserving the terminal-first direction, one shared backend contract, two supported frontends, human review, and Codex/Gemini ownership boundaries?

The structured artifact is `output.json`. This README explains how to read the JSON and what it should influence.

## What The Council Decided

The council decided that NeuroCLI should treat "state of the art" as structured, reviewable, validated AI work rather than broad autonomy. The strongest near-term features are not external connectors or background agents. The strongest near-term features are shared generated-file proposal and diff artifacts, validation-result artifacts, and workflow timeline events.

After those foundations, the council recommends improving the terminal-first workflow experience with a command palette, a stronger review lane, validation readiness, and a richer workspace intelligence panel. These features fit the existing Phase 5 direction because they make NeuroCLI feel like a repo-aware developer environment instead of a generic chat surface.

The council also recommends later features that are more advanced but should wait for safer foundations: shared git review, model profiles, lightweight prompt/workflow evals, local traces, MCP-style connector boundaries, controlled background task lanes, and productized planning or council sessions.

## How To Use The JSON

Use `output.json` as a feature roadmap input, not as an implementation command. The most important sections are `resolved_recommendations`, `risks`, `unresolved_questions`, `testing_considerations`, and `suggested_implementation_phases`.

The council's practical first implementation slice is shared proposal/diff artifacts plus a validation-result artifact. That slice directly supports the current generated-file review parity gap and gives later state-of-the-art features a durable base.

Future agents should use this output when updating `handoff/plans/current_plan.md`, `handoff/plans/phase_5_direction.md`, `handoff/coordination/shared_decisions.md`, and Codex/Gemini handoff notes. It should also guide future feature councils, especially around validation command policy, model profiles, connector permissions, and whether planning sessions should ever become app-visible product features.

## What This Does Not Authorize

This council output changes no runtime behavior. It does not authorize frontend-only diffing, arbitrary validation command execution, automatic commits, external connector implementation, or autonomous background code changes.

Any feature that changes behavior needs a Codex-defined backend or API contract first. Gemini should only handle React presentation after Codex wires the relevant integration or documents the contract. Textual can receive terminal-first controls earlier when they wrap existing safe actions, but new behavior still belongs in `neurocli_core` or an approved app-side integration over existing services.

## Validation

Validate this run from the repo root with:

`python -B handoff/agent_council/validate_council_output.py handoff/agent_council/runs/2026-05-03-practical-state-of-art-features`

The validator should confirm that this folder contains both `output.json` and `README.md`, then validate `output.json` against `handoff/agent_council/council_output_schema.json`.
