# Project Overview

This directory contains the architectural specification for a **Database Agentic System**. The system is designed to be an intelligent and autonomous intermediary that translates natural language into complex, multi-step database operations. It moves beyond simple "Text-to-SQL" to a true "Agentic" paradigm where software agents can reason about data, plan execution paths, and perform mutable operations with safety and semantic awareness.

The proposed technology stack is:

*   **Backend:** Python with FastAPI
*   **Frontend:** Vanilla JavaScript/HTML/CSS
*   **Agentic Framework:** Google's Agent Development Kit (ADK)
*   **Database Interaction:** SQLAlchemy and Google's "Gen AI Toolbox for Databases"

# Building and Running

This is a specification document, so there is no code to run yet. The implementation will follow the roadmap outlined in the `DatabaseAgenticSystem.pdf`.

**TODO:** Add build and run commands once the project is initialized.

# Development Conventions

The `DatabaseAgenticSystem.pdf` implies the following development conventions:

*   **Layered Service Architecture:** The system will decouple the user interface from the reasoning engine, and the reasoning engine from the data storage.
*   **Static and Dynamic Agents:** The system will use a hybrid approach with "Always-Needed" static agents and dynamically generated agents based on the database schema.
*   **Safety First:** For mutable data operations, the system will use restricted tooling, pre-computation validation, and human-in-the-loop confirmation.
*   **Schema RAG:** To mitigate "hallucination," the system will use a Retrieval Augmented Generation (RAG) pattern for the schema itself.
*   **Test-Driven Development:** Each milestone will conclude with the system writing comprehensive automated tests (unit, integration, and end-to-end). Manual tests will be created for scenarios that are difficult to automate.
*   **Continuous Documentation:** After each milestone, the documentation will be updated to reflect the latest changes.

# Milestones

The project will be developed in a series of 10-15 detailed milestones. Each milestone will deliver a functional component of the system and will follow the pattern of:

1.  **Implementation:** Implement the features for the milestone.
2.  **Testing:**
    *   Write comprehensive automated tests.
    *   Define and execute manual tests where necessary.
3.  **Documentation:** Update all relevant documentation.

This iterative process ensures that the project remains robust, well-tested, and well-documented at every stage.
