# Agent Council Runs

Each real council subject gets its own subfolder here.

A subject is one complete council execution across all four rounds. Do not store several unrelated subjects in one folder, and do not split one subject's rounds across separate folders.

Use this shape:

`handoff/agent_council/runs/YYYY-MM-DD-short-topic/output.json`

`handoff/agent_council/runs/YYYY-MM-DD-short-topic/README.md`

For example:

`handoff/agent_council/runs/2026-05-02-project-direction/output.json`

`handoff/agent_council/runs/2026-05-02-project-direction/README.md`

The `README.md` is required. It should discuss the JSON output in human-readable terms, including the council decision, how to use the JSON, what the JSON does not authorize, and how to validate the run.

If a subject needs extra supporting notes, keep them beside `output.json` and `README.md` inside that same subject folder.

Current real runs:

`2026-05-03-project-direction/` establishes the terminal-first direction for the next phases.

`2026-05-03-practical-state-of-art-features/` ranks practical feature candidates and identifies the shared proposal/diff artifact as the first implementation slice.
