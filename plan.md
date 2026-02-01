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

## Milestone 2: Schema Ingestion & Data Connection [IN PROGRESS]
- [ ] Objectives
    - [ ] Connect to a database via SQLAlchemy.
    - [ ] Implement schema ingestion from YAML metadata.
    - [ ] Create a Schema Registry for semantic awareness.
- [ ] Tasks
    - [ ] **Database Connection**
        - [ ] Implement `backend/core/database.py` with SQLAlchemy engine/session.
        - [ ] Configure DB URL via environment variables (default to SQLite).
    - [ ] **Schema Ingestion & Registry**
        - [ ] Define `backend/core/schema_parser.py` to read `schema.yaml`.
        - [ ] Implement `backend/core/schema_registry.py` as a singleton for metadata access.
        - [ ] Create a `data/` directory and populate it with a sample `schema.yaml`.
    - [ ] **Schema Discovery Tooling**
        - [ ] Create `backend/core/tools/schema_tools.py`.
        - [ ] Define `get_table_schema` and `list_tables` ADK-compatible tools.
        - [ ] Integrate these tools into the `OrchestratorAgent` for early testing.
- [ ] Tests
    - [ ] **Automated**
        - [ ] Test database connection health.
        - [ ] Test schema parser with valid/invalid YAML.
        - [ ] Test Schema Registry singleton behavior.
    - [ ] **Manual**
        - [ ] Confirm agent can describe the schema when asked "Which tables are available?".

## Milestone 3: ADK Integration & Root Router
- [ ] Objectives
    - [ ] Integrate Google ADK into the FastAPI backend.
    - [ ] Implement the `RootRouter` for high-level intent analysis.
- [ ] Tasks
    - [ ] Initialize ADK `LlmAgent` for the Root Router.
    - [ ] Define the base prompt for the Root Router.
    - [ ] Implement the routing logic to dispatch requests to specialized agents.
- [ ] Tests
    - [ ] Send a mock request to the Root Router and verify it correctly identifies the intent.

## Milestone 4: Read-Only Schema Exploration Agent
- [ ] Objectives
    - [ ] Enable the system to answer "What is in this database?".
    - [ ] Implement the `Read Database Schema Agent`.
- [ ] Tasks
    - [ ] Create the `ReadSchemaTool` for inspecting the Registry/Database.
    - [ ] Implement the `Read Database Schema Agent` using ADK.
    - [ ] Connect the agent to the Root Router.
- [ ] Tests
    - [ ] Ask "List all tables" and verify the agent returns the correct list.
    - [ ] Ask "Do we have a table for pilots?" and verify the response.

## Milestone 5: SQL Generation Agent & Schema RAG
- [ ] Objectives
    - [ ] Translate natural language into optimized SQL.
    - [ ] Implement RAG to prevent hallucinated columns.
- [ ] Tasks
    - [ ] Create the `SQL Generation Agent`.
    - [ ] Implement a basic retrieval mechanism (keyword/vector) for relevant schema context.
    - [ ] Develop the `ExecuteSQLTool` (Read-only mode).
- [ ] Tests
    - [ ] Query for specific data (e.g., "Show me the top 5 flights") and verify the generated SQL and results.

## Milestone 6: Reporting Agent & NL Synthesis
- [ ] Objectives
    - [ ] Transform raw database output into human-readable narratives.
- [ ] Tasks
    - [ ] Implement the `Reporting Agent`.
    - [ ] Integrate the Reporting Agent into the response pipeline.
    - [ ] Enable the agent to decide between text, lists, and tables.
- [ ] Tests
    - [ ] Verify that JSON results are summarized into natural language (e.g., "Flight 1234 departed at...").

## Milestone 7: Frontend Chat Interface
- [ ] Objectives
    - [ ] Create a modern, interactive chat UI for user interaction.
- [ ] Tasks
    - [ ] Build the chat window and message bubbles (JS/HTML).
    - [ ] Implement real-time updates for agent reasoning steps (streaming/polling).
    - [ ] Add sidebar for database status and schema overview.
- [ ] Tests
    - [ ] Manually test the chat flow from input to response.

## Milestone 8: Semantic Agent Factory
- [ ] Objectives
    - [ ] Automatically generate agents based on database domains.
- [ ] Tasks
    - [ ] Implement "Semantic Clustering" logic to group tables into domains.
    - [ ] Build the factory logic to instantiate dynamic `LlmAgent` objects.
    - [ ] Register dynamic agents with the `RootRouter`.
- [ ] Tests
    - [ ] Add new tables to the schema and verify that a new domain agent is "born".

## Milestone 9: Mutable Data Operations: Write Capabilities
- [ ] Objectives
    - [ ] Enable secure INSERT, UPDATE, and DELETE operations.
- [ ] Tasks
    - [ ] Implement the `ChangeDataTool` with write permissions.
    - [ ] Create a specialized `Database Administrator Agent`.
    - [ ] Implement pre-computation validation (SELECT before UPDATE/DELETE).
- [ ] Tests
    - [ ] Attempt to "Add a new pilot" and verify the tool constructs the correct INSERT statement.

## Milestone 10: Safety Layer & Human-in-the-Loop (HITL)
- [ ] Objectives
    - [ ] Prevent accidental data loss via mandatory confirmation.
- [ ] Tasks
    - [ ] Implement "Pause & Confirm" logic in the backend.
    - [ ] Create frontend confirmation modals with SQL preview and impact summary.
    - [ ] Implement the `ConfirmAction` endpoint.
- [ ] Tests
    - [ ] Attempt a DELETE operation and verify the system waits for user approval.

## Milestone 11: Temporal Engine & Scheduling
- [ ] Objectives
    - [ ] Enable autonomous, time-based database monitoring.
- [ ] Tasks
    - [ ] Integrate `APScheduler` with a persistent backend store.
    - [ ] Implement the `Schedule Agent` to parse CRON intents.
    - [ ] Create the "Events Management Dashboard" in the frontend.
- [ ] Tests
    - [ ] Schedule a task like "Check revenue every hour" and verify it registers.

## Milestone 12: Rule-Based Logic (Observers)
- [ ] Objectives
    - [ ] Implement "If X then Y" autonomous interventions.
- [ ] Tasks
    - [ ] Implement "Observer Jobs" that poll the database.
    - [ ] Create the Evaluator-Actor logic for rule enforcement.
    - [ ] Log all automated interventions to an "Events" log.
- [ ] Tests
    - [ ] Setup a rule "If usage > 90% then increase quota" and trigger it with mock data.

## Milestone 13: Visualization & Graphing
- [ ] Objectives
    - [ ] Render data insights as interactive charts.
- [ ] Tasks
    - [ ] Update Reporting Agent to generate JSON configurations for `Chart.js`.
    - [ ] Implement Chart.js components in the frontend.
- [ ] Tests
    - [ ] Ask "Graph the number of flights per month" and verify a bar chart is displayed.

## Milestone 14: Security Hardening & SQL Inspection
- [ ] Objectives
    - [ ] Protect against SQL injection and prompt injection.
- [ ] Tasks
    - [ ] Integrate `sqlparse` for deterministic SQL inspection.
    - [ ] Harden system prompts with explicit "No DDL" instructions.
    - [ ] Perform a security audit of all tool execution.
- [ ] Tests
    - [ ] Attempt a malicious request (e.g., "DROP TABLE users") and verify it is blocked.

## Milestone 15: Production Polish & Documentation
- [ ] Objectives
    - [ ] Finalize the system for release and public cloning.
- [ ] Tasks
    - [ ] Optimize performance and handle high-concurrency loops.
    - [ ] Finalize all documentation (README.md, API docs).
    - [ ] Prepare deployment scripts for Cloud Run.
- [ ] Tests
    - [ ] Verify the system can be cloned and run with minimal configuration.
