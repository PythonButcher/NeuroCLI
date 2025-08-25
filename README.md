# NeuroCLI
An Agentic, Terminal-Based AI Assistant for Developers.

## Overview
NeuroCLI is a Python command-line application built with the Textual TUI framework. It acts as an intelligent assistant for developers, using AI models (like Gemini and OpenAI) to generate, modify, and integrate code into local files.

## Core Architecture
The core architectural principle of NeuroCLI is a strict separation of concerns between the business logic and the user interface. This is critical for future integration of the core logic into other platforms, such as a web application.

- **`neurocli_core`:** This package is the "engine." It contains all business logic, including API calls, file handling, and diff generation. The code in this package is pure, UI-agnostic Python and does not have any dependencies on the `neurocli_app` package.

- **`neurocli_app`:** This package is the "dashboard." It contains the Textual TUI, which serves as the user interface. It imports and utilizes the logic from `neurocli_core` to present the features to the user.

## Getting Started

### Prerequisites
*(Add any prerequisites here, e.g., Python 3.10+)*

### Installation
```bash
# Installation instructions will be provided here.
pip install neurocli
```

### Running the Application
```bash
# Instructions to run the application will be provided here.
neurocli
```