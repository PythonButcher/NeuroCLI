# Agent Council Workflow

## Purpose

The Agent Council is a planning and handoff workflow for NeuroCLI. It gives future agents a reusable way to debate product, architecture, design, AI workflow, testing, and implementation topics before code changes begin.

This workflow does not change runtime behavior. It does not define new frontend or backend contracts by itself. A council output can recommend contract work, but the recommendation still has to be reviewed and implemented through normal Codex and Gemini ownership rules.

## Artifacts

The council lives in this folder:

`roles.md` defines the council members and the perspective each one must defend.

`master_prompt.md` is the reusable prompt to run a real council topic.

`council_output_schema.json` is the strict JSON Schema for final council artifacts.

`sample_output.json` is an example only. It reflects the current NeuroCLI project state, but it is not the result of a live council run unless a future agent explicitly records it as one.

`validate_council_output.py` validates a council run folder or council JSON file against the schema with only the Python standard library.

## How To Run A Real Council

Start by reading the project routing documents listed in `AGENTS.md`: `AGENTS.md`, `GEMINI.md`, `handoff/active_gate/README.md`, `handoff/plans/roadmap.md`, and `handoff/coordination/shared_decisions.md`. For frontend-sensitive work, also read `handoff/coordination/gemini_handoff.md`.

Choose one concrete topic. Good council topics are decisions such as "Should React get generated-file diff review through a shared backend proposal contract?" or "How should the Textual command palette be phased without changing workflow behavior?"

Use `master_prompt.md` as the prompt body. Fill in the topic, files reviewed, known constraints, and requested output folder. The final answer must be one JSON object that follows `council_output_schema.json`.

One subject equals one complete council run. A subject is not one round. Each subject goes through all four rounds: Independent Proposal, Critique and Challenge, Reconciliation and Prioritization, and Final Synthesis.

Save each real council subject in its own subfolder under `handoff/agent_council/runs/`. Use a dated folder name such as `2026-05-02-react-generated-file-review/`, then put the final JSON at `handoff/agent_council/runs/2026-05-02-react-generated-file-review/output.json`.

Every real council subject folder must also include a companion `README.md` created at the same time as `output.json`. The README should discuss the JSON output in human-readable terms: what the council decided, how future agents should use the JSON, what the output does not authorize, and how to validate the run. If a run needs extra supporting notes later, keep them beside `output.json` and `README.md` inside that same subject folder so the artifact stays self-contained.

## How To Validate JSON

Run `python handoff/agent_council/validate_council_output.py handoff/agent_council/sample_output.json`.

To validate a real run, pass the subject folder, such as `handoff/agent_council/runs/2026-05-02-react-generated-file-review`. The validator checks that the folder contains both `output.json` and a non-empty `README.md`, then validates `output.json` against `council_output_schema.json`. You can still validate the sample JSON directly because the sample is not a real subject folder.

## Current Council Runs

Two real council runs have already been created:

`runs/2026-05-03-project-direction/` defines the terminal-first project direction.

`runs/2026-05-03-practical-state-of-art-features/` identifies practical feature candidates and recommends starting with shared proposal/diff and validation artifacts.

Future council topics should be used for genuinely unresolved product, architecture, AI workflow, or cross-frontend decisions. Do not rerun a council just to restate the active roadmap.
