# NeuroCLI Project Documentation

## Read Order

| Need | Read |
| --- | --- |
| Work on the active goal | `active_gate/README.md` |
| Understand product direction | `plans/roadmap.md` |
| Use shared backend/API contracts | `coordination/shared_decisions.md` |
| Compare Textual and React behavior | `coordination/frontend_parity.md` |
| Confirm ownership boundaries | `coordination/codex_handoff.md` or `coordination/gemini_handoff.md` |
| Run a structured design council | `agent_council/README.md` |
| Consult historical material | `archive/README.md` only when required |

## Documentation Rules

`active_gate/README.md` is the only entrypoint for current work. Keep every current goal, scope boundary, acceptance check, verification command, and active owner inside `active_gate/`.

The active gate must be entirely forward-looking. It must never mention earlier work, prior phases, completion history, implementation history, or review history.

The roadmap defines direction, shared decisions define contracts, frontend parity records surface differences, and owner handoffs define stable responsibilities. These supporting files must not compete with the active gate as a current-status source.

Move historical material to `archive/`, repair links after moves, and do not make agents scan archives by default.
