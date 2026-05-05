# Handoff Folder

This folder is the shared documentation space for the project.
Everything that is not a root-level `README.md`, `AGENTS.md`, or `GEMINI.md` should live here.

## Purpose

- keep active plans in one place
- keep handoff notes in one place
- keep shared decisions in one place
- keep old planning docs out of the repo root
- keep compound checkpoints explicit so each phase says what users can do after the work is done

## Folder Layout

- `plans/`
  - `current_plan.md`: short status and next-step file
  - `roadmap.md`: active phased roadmap based on current project state and Agent Council outputs
- `coordination/`
  - `codex_handoff.md`: backend and integration notes
  - `gemini_handoff.md`: frontend UI-only notes
  - `shared_decisions.md`: rules and contracts both agents should follow
  - `frontend_parity.md`: documented differences between the Textual and React app surfaces
- `reference/`
  - supporting docs such as file maps
- `agent_council/`
  - reusable multi-agent planning workflow, roles, prompt, JSON schema, sample output, and validator
- `archive/`
  - older plans, idea lists, and superseded prompts that are not active work

## Read Order

1. `AGENTS.md`
2. `GEMINI.md`
3. `handoff/README.md`
4. `handoff/plans/current_plan.md`
5. `handoff/plans/roadmap.md`
6. `handoff/coordination/shared_decisions.md`
7. `handoff/coordination/frontend_parity.md`

## Rules

- keep notes concise and current
- do not keep planning files in the repo root
- add handoff context here when one agent's work changes expectations for the other
- prefer updating an existing doc over creating a new duplicate doc
- preserve the one-backend/two-frontends architecture in all future plans
- every phase and implementation slice must include a compound checkpoint: what the user can now do, which surface supports it, and which surface still cannot use it
- because Textual is the flagship app, a backend-only or React-only slice must document the missing Textual checkpoint instead of calling the product capability complete
- if Textual and React intentionally differ, update `coordination/frontend_parity.md` in the same slice
- use `agent_council/` for structured debate before large product, architecture, AI workflow, or cross-frontend implementation decisions
- keep superseded planning docs in `archive/` with clear archive status
