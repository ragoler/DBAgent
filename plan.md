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

## Milestone 6: Reporting Agent & NL Synthesis [IN PROGRESS]
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

## Milestone 12: Autonomous Monitoring (Loop Agent)
- [ ] Objectives
    - [ ] Implement "If X then Y" autonomous interventions using `LoopAgent`.
    - [ ] Continuously monitor database state until a condition is met.
- [ ] Tasks
    - [ ] **Loop Agent Setup**: Configure a `LoopAgent` that runs a "Check Status" step periodically.
    - [ ] **Termination Condition**: Define logic to break the loop (e.g., "Alert resolved").
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
