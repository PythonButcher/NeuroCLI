Excellent idea. That's the right way to refine our instructions based on observed behavior. Adding this rule to `GEMINI.md` will make my behavior more predictable and safe in the future.

Here is the updated content for your `GEMINI.md` file. I've added a new point to the "Your Persona & Behavior" section.

***

### **Updated `GEMINI.md`**

### **1. Project Overview**

-   **Name:** NeuroCLI
-   **Description:** A Python command-line application built with the Textual TUI framework. It acts as an intelligent assistant for developers, using AI models (like Gemini and OpenAI) to generate, modify, and integrate code into local files.

### **2. Core Architectural Principle: Separation of Concerns**

This is the most important rule for this project. The architecture MUST be kept separate:

-   **`neurocli_core`:** This package is the "engine." It contains all business logic (API calls, file handling, diff generation, etc.). Code in this package MUST be pure, UI-agnostic Python. It MUST NOT import from or depend on `neurocli_app`.
-   **`neurocli_app`:** This package is the "dashboard." It contains the Textual TUI, which serves as the user interface. It IMPORTS and USES the logic from `neurocli_core`.
-   **Reasoning:** This separation is critical for future integration of `neurocli_core` into a Flask/React web application.

### **3. Coding Standards & Conventions**

-   All Python code should use modern practices, including **type hints**.
-   Follow **PEP 8** style guidelines for code formatting.
-   Prioritize creating **modular, reusable, and easily testable functions**, especially within the `neurocli_core` package.

### **4. Your Persona & Behavior**

-   Act as an expert Python developer and a helpful assistant.
-   When asked to generate or modify code, always respect the core architectural principle of separating logic from the UI.
-   Your primary goal is to help build robust, maintainable, and scalable software.
-   **Never delete or modify a file unless explicitly instructed to do so.** Always confirm destructive actions before proceeding.