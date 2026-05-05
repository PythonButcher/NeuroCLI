# Project Direction Council Run

This folder contains the Agent Council run for the project-direction subject:

What should NeuroCLI become over the next three phases: a terminal-first AI development environment, a dual-surface AI coding platform, or a structured agent orchestration system for planning, editing, reviewing, and shipping code?

The canonical structured artifact is `output.json`. This README is the human-readable companion that explains how to interpret that JSON and what it should influence.

## What The Council Decided

The council recommends a layered direction. NeuroCLI should become a terminal-first AI development environment over the next three phases. The Textual app should remain the flagship surface because the strongest current workflow is repo-local, keyboard-driven, file-targeted, review-heavy, and close to git.

The council did not recommend turning NeuroCLI into a fully equal dual-surface platform yet. React remains strategically supported, but as a companion surface over the same shared capability engine rather than a separate product center. The practical meaning is that React should expose shared backend capabilities and safety guarantees where the backend supports them, while still using browser-native presentation.

The council also did not recommend making structured agent orchestration the immediate product identity. Instead, orchestration should emerge later from durable artifacts: generated proposals, diffs, risk notes, validation results, commit summaries, and council outputs. This keeps planning and handoff powerful without bypassing human review or creating premature autonomous execution.

## How To Use The JSON

Use `output.json` as strategic planning input for roadmap and handoff updates. The most important fields are `final_synthesis_summary`, `resolved_recommendations`, `major_disagreements`, `risks`, and `suggested_implementation_phases`.

The suggested next phases in the JSON are Core Loop Reliability, Shared Capability Parity, and Structured Orchestration Layer. These should be treated as planning guidance, not as completed implementation. Before any runtime change follows from this council output, Codex still needs to define or approve backend contracts, and Gemini should only handle React presentation after the relevant contract or integration handoff exists.

This run should especially influence future edits to `handoff/plans/current_plan.md`, `handoff/plans/phase_5_direction.md`, and `handoff/coordination/shared_decisions.md`. It should also inform which future council subjects are worth running, such as the exact parity rule between Textual and React or whether council artifacts should ever become an app-visible product feature.

## Boundaries

This council run changes no runtime behavior. It does not change `neurocli_core`, `api`, `neurocli_app`, or `web_client`. It does not create a new frontend or backend contract by itself.

The JSON says contract changes are required only if the project chooses to implement the recommended direction. Those future contracts would likely cover generated-file proposals, validation results, richer workflow state, risk summaries, model profiles, or productized orchestration artifacts. Codex owns that contract work.

## Validation

Validate this run from the repo root with:

`python -B handoff/agent_council/validate_council_output.py handoff/agent_council/runs/2026-05-03-project-direction`

The validator should confirm that the folder contains both this README and `output.json`, then validate the JSON against `handoff/agent_council/council_output_schema.json`.
