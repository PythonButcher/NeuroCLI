# Handoff Folder

This folder is the shared documentation space for the project.
Everything that is not a root-level `README.md`, `AGENTS.md`, or `GEMINI.md` should live here.

## Purpose

- keep active plans in one place
- keep handoff notes in one place
- keep shared decisions in one place
- keep old planning docs out of the repo root

## Folder Layout

- `plans/`
  - `current_plan.md`: short status and next-step file
  - `repair_plan.md`: main repair roadmap
  - `phase_5_direction.md`: frontend polish, feature parity, and product direction for the next phase
- `coordination/`
  - `codex_handoff.md`: backend and integration notes
  - `gemini_handoff.md`: frontend UI-only notes
  - `shared_decisions.md`: rules and contracts both agents should follow
- `reference/`
  - supporting docs such as file maps
- `archive/`
  - older plans and idea lists that are not active work

## Read Order

1. `AGENTS.md`
2. `GEMINI.md`
3. `handoff/README.md`
4. `handoff/plans/current_plan.md`
5. `handoff/coordination/shared_decisions.md`

## Rules

- keep notes concise and current
- do not keep planning files in the repo root
- add handoff context here when one agent's work changes expectations for the other
- prefer updating an existing doc over creating a new duplicate doc
- preserve the one-backend/two-frontends architecture in all future plans
