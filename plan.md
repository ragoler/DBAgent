# Database Agentic System Implementation Plan

This plan outlines the milestones for building the Database Agentic System. Each milestone includes objectives, tasks, and tests.

---

## Milestone 1: Core Scaffolding & Infrastructure [COMPLETE]
- [x] Objectives
    - [x] Establish the FastAPI backend structure.
    - [x] Setup the initial ADK orchestration layer.
    - [x] Create a premium "WOW" frontend boilerplate.
- [x] Tasks
    - [x] **Project Setup**
        - [x] Root directory organization: `backend/`, `frontend/`, `docs/`.
        - [x] Setup Python environment and `requirements.txt`.
        - [x] Create `.env.example`.
    - [x] **Backend Foundations**
        - [x] Implement `backend/main.py` with FastAPI.
        - [x] Configure CORS.
        - [x] Setup structured logging.
        - [x] Create a `/health` endpoint.
    - [x] **ADK Orchestration Layer**
        - [x] Define `backend/core/agent_manager.py`.
        - [x] Create a dummy `OrchestratorAgent`.
        - [x] Implement `/chat` endpoint.
    - [x] **Frontend "WOW" Shell**
        - [x] Create `frontend/index.html`.
        - [x] Build `frontend/style.css`.
        - [x] Implement `frontend/app.js`.
- [x] Tests
    - [x] **Automated**
        - [x] `pytest` for health and chat streaming.
    - [x] **Manual**
        - [x] Verified frontend aesthetics and interaction.

## Milestone 2: Schema Ingestion & Data Connection [COMPLETE]
- [x] Objectives
    - [x] Connect to a database via SQLAlchemy.
    - [x] Implement schema ingestion from YAML metadata.
    - [x] Create a Schema Registry for semantic awareness.
- [x] Tasks
    - [x] **Database Connection**
        - [x] Implement `backend/core/database.py` with SQLAlchemy engine/session.
        - [x] Configure DB URL via environment variables (default to SQLite).
    - [x] **Schema Ingestion & Registry**
        - [x] Define `backend/core/schema_parser.py` to read `schema.yaml`.
        - [x] Implement `backend/core/schema_registry.py` as a singleton for metadata access.
        - [x] Create a `data/` directory and populate it with a sample `schema.yaml`.
    - [x] **Schema Discovery Tooling**
        - [x] Create `backend/core/tools/schema_tools.py`.
        - [x] Define `get_table_schema` and `list_tables` ADK-compatible tools.
        - [x] Integrate these tools into the `OrchestratorAgent` for early testing.
- [x] Tests
    - [x] **Automated**
        - [x] Test database connection health.
        - [x] Test schema parser with valid/invalid YAML.
        - [x] Test Schema Registry singleton behavior.
    - [x] **Manual**
        - [x] Confirm agent can describe the schema when asked "Which tables are available?".

## Milestone 3: ADK Integration & Root Router [COMPLETE]
- [x] Objectives
    - [x] Transition from single-agent to multi-agent architecture.
    - [x] Implement the `RootRouter` to classify user intent.
    - [x] Refactor functionality into `SchemaExplorerAgent`.
- [x] Tasks
    - [x] **Agent Registry**
        - [x] Refactored `AgentManager` to use `RootRouter`.
        - [x] Created `backend/agents/` directory.
    - [x] **Schema Explorer Agent**
        - [x] Extracted "Orchestrator" logic into `backend/agents/schema_agent.py`.
    - [x] **Root Router**
        - [x] Implemented `backend/agents/root_router_agent.py`.
        - [x] Defined Intent Classification.
        - [x] Implemented delegation logic.
- [x] Tests
    - [x] **Automated**
        - [x] Verified full delegation flow E2E.
        - [x] Verified sub-agent formatting.

## Milestone 4: SQL Generation Workflow (Sequence Agent) [COMPLETE]
- [x] Objectives
    - [x] Enable the agent to answer "How many pilots are there?" or "Show me flights to Paris".
    - [x] Implement a **Sequence Agent** pipeline: `GenSQL -> Validate -> Execute`.
    - [x] Ensure READ-ONLY safety (no DROP/DELETE supported yet).
- [x] Tasks
    - [x] **SQL Tools**:
        - [x] `generate_sql_tool` (LLM-based).
        - [x] `validate_sql_tool` (using `sqlparse`/AST).
        - [x] `execute_readonly_sql_tool` (SQLAlchemy).
    - [x] **Sequence Agent**:
        - [x] Implement `backend/agents/sql_sequence_agent.py`.
        - [x] Configure the linear chain of thought.
    - [x] **Router Integration**:
        - [x] Add `delegate_to_sql_agent` tool to Root Router.
- [x] Tests
    - [x] Verify generation of valid SQL for simple queries.
    - [x] Verify validation catches syntax errors.
    - [x] Verify execution returns actual DB rows.

## Milestone 6: Reporting Agent & NL Synthesis [COMPLETE]
- [x] Objectives
    - [x] Transform raw database output into human-readable narratives.
- [x] Tasks
    - [x] Implement the `Reporting Agent`.
    - [x] Integrate the Reporting Agent into the response pipeline.
    - [x] Enable the agent to decide between text, lists, and tables.
- [x] Tests
    - [x] Verified that JSON results are summarized into natural language (e.g., "Flight 1234 departed at...").
    - [x] Added 29/29 total passing tests.

## Milestone 7: Frontend Chat Interface & Charting [IN PROGRESS]
- [x] Objectives
    - [x] Create a modern, interactive chat UI with real-time "Reasoning" feedback. [COMPLETE]
    - [x] Integrate interactive charting (**ApexCharts**). [COMPLETE]
- [x] Tasks
    - [x] Build the enhanced chat window with message bubbles. [COMPLETE]
    - [x] Implement a **Reasoning Sidebar** to show the agent's internal thought process. [COMPLETE]
    - [x] Update `app.js` to parse structured chart metadata from the agent. [COMPLETE]
    - [x] Implement dynamic ApexCharts rendering components. [COMPLETE]
    - [x] Verify charting and reasoning flow.
- [x] Tests
    - [x] Ask "Graph flights per origin" and verify a chart appears.
    - [x] Verify message streaming and reasoning steps are visible.

## Milestone 8: Observability & Granular Reasoning (OpenTelemetry) [COMPLETE]
- [x] **Objectives**
    - [x] Implement OpenTelemetry for full trace visibility (Agents -> Sub-agents -> Tools).
    - [x] Refactor the "Agent Thought Process" UI to display the full execution tree, not just the top-level agent.
    - [x] Clean up the final response by moving internal reasoning/tool calls to the sidebar.
- [x] **Tasks**
    - [x] **Backend Observability**
        - [x] Integrate `opentelemetry-instrumentation-fastapi` and `opentelemetry-sdk`.
        - [x] Instrument the `AgentManager` and `AdkAgent` classes to create spans for every agent and tool execution.
        - [x] Ensure spans include input/output data.
    - [x] **Frontend Reasoning Update**
        - [x] Update the `/chat` endpoint to stream OTel trace data (or a simplified representation of it) alongside the answer.
        - [x] Refactor `app.js` and the sidebar component to render a nested tree view of the execution trace.
        - [x] Filter out "inner monologue" text from the final user-facing message bubble.
- [x] **Tests**
    - [x] **Automated**
        - [x] Verify that spans are created for sub-agent calls.
    - [x] **Manual**
        - [x] Verify that a complex query (e.g., one that delegates to SQL agent) shows a nested trace in the sidebar.
        - [x] Verify that the final answer is clean and free of debug text.

## Milestone 9: Multi-Database Support & UI Selector [COMPLETE]
- [x] **Objectives**
    - [x] Refactor the backend to manage connections to multiple, named databases.
    - [x] Implement a UI dropdown to allow users to select the target database for their queries.
    - [x] Add a larger, more complex dataset (`movies.json`) for robust testing and demonstration.
- [x] **Tasks**
    - [x] **Backend: Multi-Engine Support**
        - [x] Create a `data/databases.yaml` config file to define multiple database connections (e.g., `flights`, `movies`).
        - [x] Modify `backend/core/database.py` to load this config and manage a dictionary of SQLAlchemy engines instead of a single one.
        - [x] Create a new `/databases` endpoint in `main.py` to return the list of available database names.
        - [x] Update the `/chat` endpoint and `AgentManager` to accept a `database_id` to route the query to the correct database engine and schema.
    - [x] **Backend: New Dataset Ingestion**
        - [x] Download the `movies.json` dataset from Vega's CDN and place it in the `data/` directory.
        - [x] Create a new script, `backend/scripts/init_movies_db.py`, to parse `movies.json` and create a `movies.db` SQLite database.
    - [x] **Frontend: Database Selector**
        - [x] In `frontend/app.js`, fetch the list of databases from the `/databases` endpoint on page load.
        - [x] In `frontend/index.html`, add a `<select>` dropdown menu to display the available databases.
        - [x] Update the `sendMessage` function in `app.js` to include the currently selected `database_id` in the payload sent to the `/chat` endpoint.
- [x] **Tests**
    - [x] **Automated**
        - [x] Add a unit test to verify the `/databases` endpoint returns the configured list.
        - [x] Add a new scenario to `test_scenarios.py` that targets the "movies" database to test the new data source.
    - [x] **Manual**
        - [x] Verify the database dropdown appears in the UI and is populated correctly.
        - [x] Select the "movies" database and ask a query like "How many movies were released in the 1990s?".
        - [x] Switch back to the "flights" database and verify it still works correctly.

## Milestone 10: Semantic Agent Factory
- [ ] Objectives
    - [ ] Automatically generate agents based on database domains.
- [ ] Tasks
    - [ ] Implement "Semantic Clustering" logic to group tables into domains.
    - [ ] Build the factory logic to instantiate dynamic `LlmAgent` objects.
    - [ ] Register dynamic agents with the `RootRouter`.
- [ ] Tests
    - [ ] Add new tables to the schema and verify that a new domain agent is "born".

## Milestone 11: Mutable Data Operations: Write Capabilities
- [ ] Objectives
    - [ ] Enable secure INSERT, UPDATE, and DELETE operations.
- [ ] Tasks
    - [ ] Implement the `ChangeDataTool` with write permissions.
    - [ ] Create a specialized `Database Administrator Agent`.
    - [ ] Implement pre-computation validation (SELECT before UPDATE/DELETE).
- [ ] Tests
    - [ ] Attempt to "Add a new pilot" and verify the tool constructs the correct INSERT statement.

## Milestone 12: Safety Layer & Human-in-the-Loop (HITL)
- [ ] Objectives
    - [ ] Prevent accidental data loss via mandatory confirmation.
- [ ] Tasks
    - [ ] Implement "Pause & Confirm" logic in the backend.
    - [ ] Create frontend confirmation modals with SQL preview and impact summary.
    - [ ] Implement the `ConfirmAction` endpoint.
- [ ] Tests
    - [ ] Attempt a DELETE operation and verify the system waits for user approval.

## Milestone 13: Temporal Engine & Scheduling
- [ ] Objectives
    - [ ] Enable autonomous, time-based database monitoring.
- [ ] Tasks
    - [ ] Integrate `APScheduler` with a persistent backend store.
    - [ ] Implement the `Schedule Agent` to parse CRON intents.
    - [ ] Create the "Events Management Dashboard" in the frontend.
- [ ] Tests
    - [ ] Schedule a task like "Check revenue every hour" and verify it registers.

## Milestone 14: Autonomous Monitoring (Loop Agent)
- [ ] Objectives
    - [ ] Implement "If X then Y" autonomous interventions using `LoopAgent`.
    - [ ] Continuously monitor database state until a condition is met.
- [ ] Tasks
    - [ ] **Loop Agent Setup**: Configure a `LoopAgent` that runs a "Check Status" step periodically.
    - [ ] **Termination Condition**: Define logic to break the loop (e.g., "Alert resolved").
    - [ ] Log all automated interventions to an "Events" log.
- [ ] Tests
    - [ ] Setup a rule "If usage > 90% then increase quota" and trigger it with mock data.

## Milestone 15: Visualization & Graphing
- [ ] Objectives
    - [ ] Render data insights as interactive charts.
- [ ] Tasks
    - [ ] Update Reporting Agent to generate JSON configurations for `Chart.js`.
    - [ ] Implement Chart.js components in the frontend.
- [ ] Tests
    - [ ] Ask "Graph the number of flights per month" and verify a bar chart is displayed.

## Milestone 16: Security Hardening & SQL Inspection
- [ ] Objectives
    - [ ] Protect against SQL injection and prompt injection.
- [ ] Tasks
    - [ ] Integrate `sqlparse` for deterministic SQL inspection.
    - [ ] Harden system prompts with explicit "No DDL" instructions.
    - [ ] Perform a security audit of all tool execution.
- [ ] Tests
    - [ ] Attempt a malicious request (e.g., "DROP TABLE users") and verify it is blocked.

## Milestone 17: Production Polish & Documentation
- [ ] Objectives
    - [ ] Finalize the system for release and public cloning.
- [ ] Tasks
    - [ ] Optimize performance and handle high-concurrency loops.
    - [ ] Finalize all documentation (README.md, API docs).
    - [ ] Prepare deployment scripts for Cloud Run.
- [ ] Tests
    - [ ] Verify the system can be cloned and run with minimal configuration.
