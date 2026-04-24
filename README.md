# NeuroCLI

NeuroCLI has two supported app paths:

- a Python Textual app in `neurocli_app`
- a React web app in `web_client`

Both should use the same shared backend logic from `neurocli_core`.

## Getting Started

### Requirements

- Python 3.10+
- an OpenAI API key in the project `.env` file

Example:

```bash
OPENAI_API_KEY=sk-your-key
```

### Install

```bash
pip install -e .
```

### Run The Python App

```bash
neurocli
```

## Project Docs

Project planning and handoff docs live in `handoff/`.

Start with:

- `handoff/README.md`
- `handoff/plans/current_plan.md`
- `handoff/plans/repair_plan.md`
