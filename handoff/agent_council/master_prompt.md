# Master Agent Council Prompt

You are running the NeuroCLI Agent Council. This is a planning and handoff exercise only. Do not modify runtime application behavior, do not change frontend or backend contracts, and do not remove, simplify, or downgrade existing functionality.

Project context: NeuroCLI has one shared Python backend workflow in `neurocli_core`, a Python Textual frontend in `neurocli_app`, a FastAPI bridge in `api`, and a React frontend in `web_client`. Codex owns backend, Python, API, shared logic, and React integration logic. Gemini owns React UI and presentation only. Shared decisions and handoffs live under `handoff/`.

Council topic: [replace this with one specific topic]

Files and sources reviewed: [list the exact docs and code files reviewed]

Known constraints: [list project-specific constraints, active phase notes, ownership boundaries, and testing limits]

Requested output folder: [replace this with a folder such as `handoff/agent_council/runs/2026-05-02-project-direction/`]

Participating roles: Architecture Guardian, Product/UX Strategist, AI Workflow Steward, Skeptic/QA Reviewer, Implementation Planner, and Frontend Parity Advocate.

Round One is Independent Proposal. Each role must independently state what should be added, improved, removed, reconsidered, and protected. Each role must make its reasoning concrete by naming affected NeuroCLI areas where possible.

Round Two is Critique and Challenge. Each role must challenge at least two other positions. The critique must identify assumptions, risks, missing evidence, ownership problems, contract ambiguity, or testing gaps.

Round Three is Reconciliation and Prioritization. The council must reconcile compatible ideas, keep meaningful disagreements visible, defer weak ideas, and prioritize recommendations. The council must not hide unresolved questions behind vague consensus.

Round Four is Final Synthesis. Produce exactly one JSON object and no surrounding prose. The JSON must validate against `handoff/agent_council/council_output_schema.json`. Save the JSON as `output.json` inside the requested subject folder. Include project context, files or sources reviewed, participating agents, conversation rounds, major disagreements, resolved recommendations, unresolved questions, risks, impacted areas, frontend implications, backend implications, contract considerations, testing considerations, implementation priority, suggested implementation phases, and final synthesis summary.

At the same time, create a companion `README.md` in the same subject folder. The README must discuss the JSON output in human-readable terms: what the council decided, how future agents should use the JSON, what the output does not authorize, and how to validate the run. This README is required for every real council subject and must stay beside `output.json`.

The final JSON must be specific to NeuroCLI. It must distinguish documentation-only planning from runtime behavior. It must call out whether any future implementation would require changes in `neurocli_core`, `api`, `neurocli_app`, or `web_client`. If the council recommends frontend work that depends on backend data or payload changes, it must say that Codex must define or approve the contract before Gemini presentation work proceeds.
