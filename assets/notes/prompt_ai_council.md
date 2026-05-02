# Agent Council Workflow Setup

This document outlines the process for setting up an Agent Council workflow for this project. The workflow should be adapted to the project's existing architecture, development process, and documentation style, rather than assuming a direct fit from another project.

## Objective

The primary goal is to establish a reusable planning and debate system. This system will enable multiple AI sub-agents to examine proposed product, engineering, design, architecture, or implementation topics from diverse perspectives. They will challenge one another, reconcile disagreements, and ultimately produce a structured JSON artifact for subsequent AI analysis.

## Core Principles and Constraints

This Agent Council is strictly a **planning and handoff system only**. It is crucial to adhere to the following constraints:

*   Do not modify runtime application behavior.
*   Do not change frontend or backend contracts.
*   Do not remove, simplify, or downgrade existing functionality.

## Required Artifacts

To implement this workflow, the following core artifacts must be created:

*   An agent roles definition.
*   A master council prompt.
*   A strict JSON output schema.
*   A realistic sample output.
*   Usage documentation.
*   A lightweight validator (if it fits the project).

These artifacts should be placed within the project’s existing documentation or planning area. If the project has an active documentation index, status file, agent instructions, or handoff registry, the new workflow should be linked there.

## Council Definition and Roles

The council must be defined with distinct perspectives that actively challenge each other. It must include at least the following roles:

*   **Architecture Guardian**: Focuses on system integrity, scalability, and long-term maintainability.
*   **Product/UX Strategist**: Represents user needs, market fit, and overall product vision.
*   **Domain Specialist**: Adapted to this project’s actual domain. (e.g., Data Specialist, AI Ethicist, Security Expert, Infrastructure Lead, Design Lead, etc., depending on project risks).
*   **Skeptic/QA Reviewer**: Challenges assumptions, identifies potential flaws, and ensures quality.
*   **Implementation Planner**: Considers feasibility, resource allocation, and practical execution.

Additional roles should be added or existing roles renamed if the project is data-heavy, AI-heavy, design-heavy, infrastructure-heavy, or security-sensitive, to reflect the real risks of the project.

## Council Process: Four Rounds

The council process will be structured into four distinct rounds:

### Round One: Independent Proposal

Each agent independently proposes what should be:

*   Added
*   Improved
*   Removed
*   Reconsidered
*   Protected

### Round Two: Critique and Challenge

Agents critique one another’s ideas, focusing on:

*   Challenging assumptions.
*   Identifying risks.
*   Surfacing disagreements.

### Round Three: Reconciliation and Prioritization

Agents work to reconcile the strongest ideas, engaging in:

*   Debating disagreements.
*   Combining compatible proposals.
*   Deferring weak ideas.
*   Prioritizing recommendations.

### Round Four: Final Synthesis

The discussion is synthesized into a final structured JSON output, designed for downstream AI analysis.

## JSON Output Design

The JSON output should be designed to capture comprehensive information, including:

*   **Project Context**: Overview of the project.
*   **Files or Sources Reviewed**: References to relevant documents or code.
*   **Participating Agents**: List of agents involved in the discussion.
*   **Conversation Rounds**: Summary or log of each round's key points.
*   **Major Disagreements**: Identified points of contention.
*   **Resolved Recommendations**: Agreed-upon actions or decisions.
*   **Unresolved Questions**: Open items requiring further investigation.
*   **Risks**: Potential issues and their impact.
*   **Impacted Areas of the Codebase**: Specific modules or components affected.
*   **Frontend Implications**: Relevant considerations for the user interface.
*   **Backend Implications**: Relevant considerations for server-side logic.
*   **Contract Considerations**: Changes or impacts on APIs, data models, etc.
*   **Testing Considerations**: Requirements for testing and validation.
*   **Implementation Priority**: Level of urgency for implementation.
*   **Suggested Implementation Phases**: Breakdown of work into stages.
*   **Final Synthesis Summary**: A concise overview of the council's conclusions.

## Sample Output and Validation

A realistic sample council output, reflecting the project’s current state, must be created. It should be clearly stated that this sample is an example only, unless it is the result of an explicitly run council topic.

If a validator for the JSON output schema is added, the sample JSON should be validated against it.

## Summary and Next Steps

Upon completion of this workflow setup, the following will be available:

*   **What was added**: Agent roles definition, master council prompt, strict JSON output schema, realistic sample output, usage documentation, and an optional lightweight validator.
*   **Where the files live**: (To be specified based on project structure, e.g., `docs/agent_council/`).
*   **How to run a real council**: (To be detailed in usage documentation).
*   **How to validate the JSON**: (To be detailed in usage documentation, referencing the validator).
*   **Good first council topic**: (A specific, relevant topic for this project to initiate the workflow).