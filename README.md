# NeuroCLI
An Agentic, Terminal-Based AI Assistant for Developers.

## Overview
NeuroCLI is a Python command-line application built with the Textual TUI framework. It acts as an intelligent assistant for developers, using OpenAI models to generate, modify, and integrate code into local files.

## Core Architecture
The core architectural principle of NeuroCLI is a strict separation of concerns between the business logic and the user interface. This is critical for future integration of the core logic into other platforms, such as a web application.

- **`neurocli_core`:** This package is the "engine." It contains all business logic, including API calls, file handling, and diff generation. The code in this package is pure, UI-agnostic Python and does not have any dependencies on the `neurocli_app` package.

- **`neurocli_app`:** This package is the "dashboard." It contains the Textual TUI, which serves as the user interface. It imports and utilizes the logic from `neurocli_core` to present the features to the user.

## Getting Started

### Prerequisites
* Python 3.10+
* Git 2.30+ available on your `PATH` for the Git-assisted workflow
* (Optional) An `$EDITOR` environment variable if you want to open files from NeuroCLI
* An OpenAI API key stored in a project-level `.env` file:

  ```bash
  OPENAI_API_KEY=sk-your-key
  ```

### Installation
```bash
pip install -e .
```

### Running the Application
```bash
neurocli
```

## Git-Enabled Workflow

NeuroCLI can now surface Git information and apply AI-generated patches directly through `git apply`.

1. Select a file in the `file_path` input (or via **Browse...**) before submitting a prompt.
2. After the diff is generated, use **Apply Changes** to choose between:
   * **Apply (Working Tree)** – applies the diff with `git apply`. When the selected file is outside a Git repository, NeuroCLI falls back to writing the new content directly to disk so you never lose the proposal.
   * **Apply & Stage** – applies the diff and stages the file with `git add`.
3. Use **Stage Diff** at any time to stage the current file, and **Open in $EDITOR** to jump into your configured editor without leaving the TUI.

### Safeguards and Status Feedback

* The Git status panel automatically targets the selected file and displays the current branch and `git status --short` output.
* When no repository is detected, staging actions are disabled, and the Apply workflow transparently writes to disk without invoking Git.
* Errors and successes from Git helpers appear inline in the AI response panel so you can confirm each step.
