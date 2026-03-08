#!/bin/bash
set -e

# Default Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-west1"
CLUSTER_NAME="adk-cluster"
REPO_NAME="dbagent-repo"
IMAGE_NAME="db-agent"
TAG="latest"
GSA_NAME="dbagent-gsa"
APP_NAME="db-agent"
NAMESPACE="dev"

# Internal variables
LOCAL_BUILD=false
DELETE_RESOURCES=false
SKIP_INFRA=false
ENV_VARS=()

show_help() {
  cat <<EOF
Usage: ./deploy.sh [OPTIONS]

Options:
  --local             Build the Docker image locally instead of using Cloud Build.
  --no-infra          Skip infrastructure setup (IAM, Repo, Secrets).
  -e NAME=VALUE       Pass environment variables to the build process.
  --delete            Teardown all resources created by this script.
  --namespace         Target namespace (dev or prod). Default: dev.
  --help              Show this help message.
EOF
}

# Argument parsing
while [[ $# -gt 0 ]]; do
  case $1 in
    --local)
      LOCAL_BUILD=true
      shift
      ;;
    --no-infra)
      SKIP_INFRA=true
      shift
      ;;
    --delete)
      DELETE_RESOURCES=true
      shift
      ;;
    --namespace)
      NAMESPACE="$2"
      shift 2
      ;;
    -e)
      if [[ -n "$2" ]]; then
        ENV_VARS+=(--build-arg "$2")
        shift 2
      else
        echo "Error: -e requires an argument (NAME=VALUE)."
        exit 1
      fi
      ;;
    --help)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [[ "$NAMESPACE" != "dev" && "$NAMESPACE" != "prod" ]]; then
    echo "Error: --namespace must be either 'dev' or 'prod'"
    exit 1
fi

GSA_EMAIL="$GSA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
KSA_NAME="dbagent-ksa-$NAMESPACE"

# --- Teardown Logic ---
if [ "$DELETE_RESOURCES" == "true" ]; then
  echo "Deleting all cloud resources for namespace $NAMESPACE..."
  
  if gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION; then
    echo "Deleting Kubernetes resources in namespace $NAMESPACE..."
    # Substitute and delete
    sed -e "s|\${APP_NAME}|$APP_NAME|g" \
        -e "s|\${NAMESPACE}|$NAMESPACE|g" \
        -e "s|\${IMAGE_URL}|ignored|g" \
        -e "s|\${KSA_NAME}|$KSA_NAME|g" k8s/deployment.yaml k8s/service.yaml | kubectl delete -f - --ignore-not-found=true
    
    kubectl delete secret db-agent-secrets -n $NAMESPACE --ignore-not-found=true
    kubectl delete serviceaccount $KSA_NAME -n $NAMESPACE --ignore-not-found=true
    kubectl delete namespace $NAMESPACE --ignore-not-found=true
  fi

  echo "Removing IAM policy bindings..."
  # Clean up Workload identity binding for this namespace
  gcloud iam service-accounts remove-iam-policy-binding $GSA_EMAIL \
    --role="roles/iam.workloadIdentityUser" \
    --member="serviceAccount:$PROJECT_ID.svc.id.goog[$NAMESPACE/$KSA_NAME]" --quiet || echo "IAM binding for WIP not found."
  
  echo "Deleting Google Service Account..."
  gcloud iam service-accounts delete $GSA_EMAIL --quiet || echo "GSA not found or already deleted."

  echo "Deleting Artifact Registry repository..."
  gcloud artifacts repositories delete $REPO_NAME --location=$REGION --quiet || echo "Repo not found or deleted."
  
  exit 0
fi

echo "Using Project ID: $PROJECT_ID"
echo "Targeting Namespace: $NAMESPACE"

if [ "$SKIP_INFRA" == "false" ]; then
    echo "Enabling required APIs..."
    gcloud services enable container.googleapis.com \
        artifactregistry.googleapis.com \
        cloudbuild.googleapis.com \
        aiplatform.googleapis.com

    add_iam_binding() {
        local MAX_RETRIES=5
        local RETRY_DELAY=2
        local COUNT=0
        
        while [ $COUNT -lt $MAX_RETRIES ]; do
            echo "Granting $3 to $2 (Attempt $((COUNT+1)))..."
            if gcloud projects add-iam-policy-binding "$1" \
                --member="$2" \
                --role="$3" --quiet > /dev/null; then
                return 0
            fi
            sleep $RETRY_DELAY
            RETRY_DELAY=$((RETRY_DELAY * 2))
            COUNT=$((COUNT + 1))
        done
        echo "Warning: Failed to add IAM binding $3 to $2"
    }

    PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
    COMPUTE_SERVICE_ACCOUNT="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

    add_iam_binding $PROJECT_ID "serviceAccount:$COMPUTE_SERVICE_ACCOUNT" "roles/storage.admin"
    add_iam_binding $PROJECT_ID "serviceAccount:$COMPUTE_SERVICE_ACCOUNT" "roles/storage.objectViewer"
    add_iam_binding $PROJECT_ID "serviceAccount:$COMPUTE_SERVICE_ACCOUNT" "roles/artifactregistry.writer"
    add_iam_binding $PROJECT_ID "serviceAccount:$COMPUTE_SERVICE_ACCOUNT" "roles/logging.logWriter"
    add_iam_binding $PROJECT_ID "serviceAccount:$COMPUTE_SERVICE_ACCOUNT" "roles/container.defaultNodeServiceAccount"

    CLOUD_BUILD_SA_LEGACY="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
    CLOUD_BUILD_SA_MODERN="service-${PROJECT_NUMBER}@gcp-sa-cloudbuild.iam.gserviceaccount.com"

    add_iam_binding $PROJECT_ID "serviceAccount:$CLOUD_BUILD_SA_LEGACY" "roles/artifactregistry.writer"
    add_iam_binding $PROJECT_ID "serviceAccount:$CLOUD_BUILD_SA_MODERN" "roles/artifactregistry.writer"
    add_iam_binding $PROJECT_ID "serviceAccount:$CLOUD_BUILD_SA_LEGACY" "roles/storage.admin"
    add_iam_binding $PROJECT_ID "serviceAccount:$CLOUD_BUILD_SA_MODERN" "roles/storage.admin"

    if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION &>/dev/null; then
        echo "Creating Artifact Registry repository..."
        gcloud artifacts repositories create $REPO_NAME \
            --repository-format=docker \
            --location=$REGION \
            --description="Docker repository for DBAgent"
    fi
fi

echo "Getting GKE credentials for $CLUSTER_NAME..."
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

if ! kubectl get namespace $NAMESPACE &>/dev/null; then
    echo "Creating namespace $NAMESPACE..."
    kubectl create namespace $NAMESPACE
fi

if [ "$SKIP_INFRA" == "false" ]; then
    echo "Creating/Updating Kubernetes Secret from .env..."
    if [ -f backend/.env ]; then
        cp backend/.env .env.tmp
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i "" "s/GOOGLE_CLOUD_PROJECT=.*/GOOGLE_CLOUD_PROJECT=$PROJECT_ID/" .env.tmp
        else
            sed -i "s/GOOGLE_CLOUD_PROJECT=.*/GOOGLE_CLOUD_PROJECT=$PROJECT_ID/" .env.tmp
        fi
        kubectl create secret generic db-agent-secrets --from-env-file=.env.tmp --namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
        rm .env.tmp
    else
        echo "Warning: .env file not found, skipping secret creation."
    fi

    if ! gcloud iam service-accounts describe $GSA_EMAIL &>/dev/null; then
        echo "Creating Google Service Account $GSA_NAME..."
        gcloud iam service-accounts create $GSA_NAME --display-name="DBAgent Service Account"
        sleep 10
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/aiplatform.user"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/cloudbuild.builds.builder"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/container.developer"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/artifactregistry.writer"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/iam.serviceAccountUser"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/logging.logWriter"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/storage.admin"
    else
        echo "Google Service Account $GSA_NAME already exists."
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/aiplatform.user"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/cloudbuild.builds.builder"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/container.developer"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/artifactregistry.writer"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/iam.serviceAccountUser"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/logging.logWriter"
        add_iam_binding $PROJECT_ID "serviceAccount:$GSA_EMAIL" "roles/storage.admin"
    fi

    if ! kubectl get sa $KSA_NAME -n $NAMESPACE &>/dev/null; then
        echo "Creating Kubernetes Service Account $KSA_NAME in $NAMESPACE..."
        kubectl create serviceaccount $KSA_NAME --namespace $NAMESPACE
    fi

    if ! kubectl get rolebinding deployer-binding -n $NAMESPACE &>/dev/null; then
        echo "Creating Kubernetes RoleBinding for GSA in namespace $NAMESPACE..."
        kubectl create rolebinding deployer-binding \
            --clusterrole=edit \
            --user="$GSA_EMAIL" \
            --namespace=$NAMESPACE
    fi
    echo "Binding GSA to KSA via Workload Identity for $NAMESPACE..."
    gcloud iam service-accounts add-iam-policy-binding $GSA_EMAIL \
        --role="roles/iam.workloadIdentityUser" \
        --member="serviceAccount:$PROJECT_ID.svc.id.goog[$NAMESPACE/$KSA_NAME]"

    kubectl annotate serviceaccount $KSA_NAME --namespace $NAMESPACE \
        iam.gke.io/gcp-service-account=$GSA_EMAIL --overwrite
fi

IMAGE_URL="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:$TAG"
STAGING_BUCKET="gs://${PROJECT_ID}-build-staging"

if [ "$LOCAL_BUILD" == "true" ]; then
    echo "Building and pushing image to $IMAGE_URL using local Docker..."
    gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
    docker build --network host "${ENV_VARS[@]}" -t $IMAGE_URL .
    docker push $IMAGE_URL
else
    echo "Building and pushing image to $IMAGE_URL using Cloud Build..."
    if ! gsutil ls -b $STAGING_BUCKET &>/dev/null; then
        gsutil mb -l $REGION $STAGING_BUCKET
    fi
    BUILD_ID=$(gcloud builds submit . \
        --tag $IMAGE_URL \
        --gcs-source-staging-dir="$STAGING_BUCKET/source" \
        --gcs-log-dir="$STAGING_BUCKET/logs" \
        --async \
        --format="value(id)")
    
    echo "Waiting for build $BUILD_ID to finish..."
    while true; do
        STATUS=$(gcloud builds describe $BUILD_ID --format="value(status)")
        case $STATUS in
            "SUCCESS") echo "Build finished successfully!"; break ;;
            "FAILURE"|"INTERNAL_ERROR"|"TIMEOUT"|"CANCELLED") echo "Build failed: $STATUS"; exit 1 ;;
            *) sleep 10 ;;
        esac
    done
fi

echo "Deploying to Kubernetes in namespace $NAMESPACE..."
sed -e "s|\${APP_NAME}|$APP_NAME|g" \
    -e "s|\${NAMESPACE}|$NAMESPACE|g" \
    -e "s|\${IMAGE_URL}|$IMAGE_URL|g" \
    -e "s|\${KSA_NAME}|$KSA_NAME|g" \
    k8s/deployment.yaml k8s/service.yaml > k8s/rendered.yaml

kubectl apply -f k8s/rendered.yaml
rm k8s/rendered.yaml

echo "Restarting deployment..."

echo "Deployment complete for $NAMESPACE namespace!"
