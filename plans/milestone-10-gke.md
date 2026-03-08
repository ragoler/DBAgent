# Objective
Deploy the Database Agentic System to Google Kubernetes Engine (GKE). This involves containerizing the application, automating the infrastructure creation, and implementing a deployment pipeline using Cloud Build and `kubectl`.

# Key Files & Context

## Containerization
-   `Dockerfile` (New): Defines the container image for the application, including Python backend and static frontend files.
-   `.dockerignore` (New): Excludes unnecessary files from the build context.

## Infrastructure & Deployment
-   `infra.sh` (New): Shell script to:
    -   Enable necessary Google Cloud APIs (container, cloudbuild).
    -   Create a GKE Autopilot cluster.
    -   Configure `kubectl` credentials.
-   `deploy.sh` (New): Shell script to:
    -   Submit a build to Cloud Build.
    -   Deploy the container to the GKE cluster using `kubectl` (deployment + service).
-   `k8s/deployment.yaml` (New): Kubernetes Deployment manifest.
-   `k8s/service.yaml` (New): Kubernetes Service manifest (LoadBalancer).

## Documentation
-   `plan.md`: Update to reflect the new GKE Deployment milestone.

# Implementation Steps

1.  **Containerization**
    -   Create `.dockerignore`.
    -   Create `Dockerfile`:
        -   Use official Python base image (e.g., `python:3.11-slim`).
        -   Copy `backend/` and `frontend/`.
        -   Install dependencies from `backend/requirements.txt`.
        -   Expose port 8000.
        -   CMD to run `uvicorn backend.main:app --host 0.0.0.0 --port 8000`.

2.  **Kubernetes Manifests**
    -   Create `k8s/deployment.yaml`:
        -   Define Deployment `db-agent`.
        -   Replicas: 1.
        -   Container image: `gcr.io/PROJECT_ID/db-agent:latest` (placeholder).
        -   Env vars: `DB_URL`, `OPENAI_API_KEY`, etc. (ConfigMap/Secret placeholders).
    -   Create `k8s/service.yaml`:
        -   Define Service `db-agent-service`.
        -   Type: LoadBalancer.
        -   Port 80 -> Target 8000.

3.  **Infrastructure Script (`infra.sh`)**
    -   Add `gcloud services enable` commands.
    -   Add `gcloud container clusters create-auto` command.
    -   Add `gcloud container clusters get-credentials`.

4.  **Deployment Script (`deploy.sh`)**
    -   Add `gcloud builds submit --tag gcr.io/$PROJECT_ID/db-agent .`.
    -   Add `kubectl apply -f k8s/`.
    -   Add logic to substitute `PROJECT_ID` in manifests if needed (or use `envsubst`).

5.  **Project Plan Update**
    -   Insert "Milestone 10: GKE Deployment" into `plan.md`.
    -   Renumber subsequent milestones.

# Verification & Testing

## Manual Verification
1.  **Build**: Run `docker build -t db-agent .` locally to ensure Dockerfile is valid.
2.  **Infra**: Run `./infra.sh` (dry-run or actual execution if credentials available) to verify gcloud commands.
3.  **Deploy**: Run `./deploy.sh` and verify the Cloud Build submission and kubectl application.
4.  **Access**: Access the external IP of the LoadBalancer and verify the UI loads.
