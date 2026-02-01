# Database Agentic System

## Development Setup

1. **Create Virtual Environment:**
   ```bash
   python3 -m venv .venv
   ```

2. **Activate and Install Dependencies:**
   ```bash
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```

3. **Configure Environment:**
   Create a `backend/.env` file based on `backend/.env.example`.

## Running Tests

To run the automated tests:
```bash
source .venv/bin/activate
pytest backend/tests/test_main.py
```

## Running the Application

1. **Start the Unified Server:**
   ```bash
   python3 run.py
   ```

2. **Access the UI:**
   Open [http://localhost:8000](http://localhost:8000) in your browser.

The `run.py` script automatically configures the environment and serves both the API and the Frontend.

## Example Questions (by Milestone)

You can explore the system's capabilities using these sample queries in the Chat UI:

### 🔍 Schema Discovery (Milestone 2 & 3)
*   *"What tables are available in the database?"*
*   *"Describe the flights table."*
*   *"Which table contains pilot licensing information?"*

### 📊 Data Retrieval & SQL (Milestone 4)
*   *"How many flights are there in the database?"*
*   *"Show me all flights departing from JFK."*
*   *"Which plane is being used for the flight to CDG?"*
*   *"List all pilots with a Military license."*

### 📈 Advanced Reporting (Milestone 6)
*   *"Give me a high-level status report of the database."*
*   *"Summarize our current inventory of planes and pilots."*
*   *"Provide a summary of all flights scheduled for November."*

## Developer Transparency: SQL Logging
When the application is running, check your **terminal** to see the raw SQL queries being generated and executed by the agents in real-time. Look for the `--- EXECUTING SQL ---` blocks!
