#!/bin/bash
set -e

echo "========================================================"
echo " Database Agentic System: GitHub Repo Setup (Stream D) "
echo "========================================================"

# Make sure the user is authenticated with GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed. Please install it first."
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "Error: You are not authenticated with GitHub CLI. Please run 'gh auth login' first."
    exit 1
fi

echo "1. Creating 'dev' branch and pushing upstream..."
git checkout -b dev || git checkout dev
git push -u origin dev

echo "2. Setting 'dev' as the default branch..."
gh repo edit --default-branch dev

# We need to get the owner and repo name dynamically from the remote
REPO_INFO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

echo "3. Establishing branch protection for 'main'..."
echo "   - Restrict direct pushes"
echo "   - Require a pull request with passing status checks (from dev-pipeline)"
echo "   - Require human approval on PRs"

# Note: This requires admin access to the repository
gh api -X PUT "repos/${REPO_INFO}/branches/main/protection" \
  -H "Accept: application/vnd.github.v3+json" \
  -F enforce_admins=true \
  -F "required_pull_request_reviews[required_approving_review_count]=1" \
  -F "required_status_checks[strict]=true" \
  -f "required_status_checks[contexts][]=dev-pipeline" \
  -F restrictions=null

echo "========================================================"
echo " GitHub Repo Setup Complete! "
echo "========================================================"
