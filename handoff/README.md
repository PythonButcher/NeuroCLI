# NeuroCLI Project Documentation

This directory contains active project truth, ownership handoffs, reusable planning artifacts, and clearly separated history.

## Read Order

| Need | Read |
| --- | --- |
| Current status and next slice | `plans/current_plan.md` |
| Full phased direction | `plans/roadmap.md` |
| Shared backend/API contracts | `coordination/shared_decisions.md` |
| Textual and React differences | `coordination/frontend_parity.md` |
| Codex-owned integration notes | `coordination/codex_handoff.md` |
| Gemini-owned presentation notes | `coordination/gemini_handoff.md` |
| Structured design council | `agent_council/README.md` |
| Historical context | `archive/README.md` |

## Documentation Rules

`plans/current_plan.md` is the only current status source. The roadmap defines phase order; shared decisions define contracts; frontend parity records intentional surface differences.

Keep active files concise. Move superseded plans and completed implementation diaries to `archive/`, fix links after moves, and do not make agents scan historical material by default.

Every completed slice must record its compound checkpoint: the new user-visible capability, its available surface, the supporting backend/API contract, and any remaining surface gap.
