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

## Deployment & CI/CD Workflow (GKE)

Because Google Cloud Organization Policies currently block GitHub Actions from automatically deploying (via Workload Identity Federation or Service Account JSON Keys), you must trigger deployments manually from an authenticated local terminal. 

### 1. Developing and Deploying to `dev`
When you are actively building new features or testing:
1. **Write Code on `dev`:** Make sure you are on your local `dev` branch (`git checkout dev`).
2. **Commit to GitHub:** When ready, push your code to the remote repository.
   ```bash
   git add .
   git commit -m "Added a new feature"
   git push origin dev
   ```
3. **Deploy to GKE `dev`:** Run the deploy script from your terminal. This archives your code, builds the container via Google Cloud Build, and applies the Kubernetes manifests to the `dev` namespace:
   ```bash
   ./deploy.sh --namespace dev --no-infra
   ```
4. **Verify `dev`:** Wait a few moments, and verify your changes on the `dev` IP address (fetch via `kubectl get services -n dev`).

### 2. Promoting and Deploying to `prod` (main)
When you are completely satisfied that `dev` is stable and you want to release it to production:
1. **Merge to `main`:** 
   ```bash
   git checkout main
   git merge dev
   git push origin main
   ```
2. **Switch back to `dev` (Important!):** Always move your local terminal back to development so you don't accidentally write future code directly to `main`.
   ```bash
   git checkout dev
   ```
3. **Deploy to GKE `prod`:** Now that the production `main` branch is updated on GitHub, deploy to the strictly segregated `prod` Kubernetes environment.
   ```bash
   ./deploy.sh --namespace prod --no-infra
   ```
4. **Verify `prod`:** Use `kubectl get services -n prod` to see the production LoadBalancer IP address!

*Note: Once your Org Admin grants an exception to `constraints/iam.workloadIdentityPoolProviders` or `constraints/iam.disableServiceAccountKeyCreation`, GitHub Actions will begin running these deploy scripts automatically on push/merge.*
