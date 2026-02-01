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
