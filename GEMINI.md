# GEMINI.md - NeuroCLI AI Assistant Instructions

## 1. Project Overview

-   **Name:** NeuroCLI
-   **Description:** A command-line application built with Python and the Textual TUI framework. It acts as an intelligent assistant for developers, using AI models (like Gemini and OpenAI) to process, generate, modify, and integrate code into local files.
-   **Goal:** The primary goal of NeuroCLI is to be a versatile development tool **capable of working with many different file types across various languages and frameworks, not just Python.** Its intelligent features should be designed to handle general text processing, code formatting, and code modifications for any standard development file, such as Javascript, CSS, HTML, Markdown, and more.

## 2. Core Architectural Principle: Separation of Concerns

This is the most important rule for this project. The architecture MUST be kept separate:

-   **`neurocli_core`:** This package is the "engine." It contains all business logic (API calls, file handling, diff generation, code processing, etc.). Code in this package MUST be pure, UI-agnostic Python. It MUST NOT import from or depend on `neurocli_app`.
-   **`neurocli_app`:** This package is the "dashboard." It contains the Textual TUI, which serves as the user interface. It IMPORTS and USES the logic from `neurocli_core`.
-   **Reasoning:** This separation is critical for future integration of `neurocli_core` into web applications or other frontends, ensuring maximum reusability.

## 3. Coding Standards & Conventions

-   All Python code should use modern practices, including **type hints**.
-   Follow **PEP 8** style guidelines for code formatting.
-   Prioritize creating **modular, reusable, and easily testable functions**, especially within the `neurocli_core` package.
-   Always consider multi-language support when writing core logic (e.g., using appropriate formatters or syntax highlighters based on file extensions).

## 4. Your Persona & Behavior

-   Act as an expert software developer and a helpful assistant.
-   When asked to generate or modify code, always respect the core architectural principle of separating logic from the UI.
-   Your primary goal is to help build robust, maintainable, scalable, and versatile software that handles diverse project needs.
-   **Never delete or modify a file unless explicitly instructed to do so.** Always confirm destructive actions before proceeding.