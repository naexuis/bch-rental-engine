#!/usr/bin/env bash

###############################################################################
# BCH Rental Engine
# Update Dashboard
###############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}/config.sh"
source "${SCRIPT_DIR}/common.sh"

print_banner "Update Dashboard"

cd "${PROJECT_DIR}"

echo -e "${BLUE}Project Directory:${NC} ${PROJECT_DIR}"
echo -e "${BLUE}Branch:${NC}            $(git branch --show-current)"
echo -e "${BLUE}Current Commit:${NC}    $(git rev-parse --short HEAD)"
echo

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "${RED}ERROR:${NC} The Git working tree contains uncommitted changes."
    echo
    git status --short
    echo
    echo "Commit, stash, or discard the changes before updating."
    exit 1
fi

CURRENT_BRANCH="$(git branch --show-current)"

if [[ -z "${CURRENT_BRANCH}" ]]; then
    echo -e "${RED}ERROR:${NC} The repository is in detached HEAD state."
    exit 1
fi

echo "Fetching updates from origin..."
git fetch origin "${CURRENT_BRANCH}"

LOCAL_COMMIT="$(git rev-parse HEAD)"
REMOTE_COMMIT="$(git rev-parse "origin/${CURRENT_BRANCH}")"

if [[ "${LOCAL_COMMIT}" == "${REMOTE_COMMIT}" ]]; then
    echo -e "${GREEN}Repository is already up to date.${NC}"
else
    echo "Pulling the latest changes..."
    git pull --ff-only origin "${CURRENT_BRANCH}"
    echo -e "${GREEN}Repository updated successfully.${NC}"
fi

echo
echo -e "${BLUE}Updated Commit:${NC} $(git rev-parse --short HEAD)"
echo

echo "Building the dashboard image..."
"${SCRIPT_DIR}/build_dashboard.sh"

echo
echo "Deploying the dashboard..."
"${SCRIPT_DIR}/deploy_dashboard.sh"

echo
echo -e "${GREEN}Dashboard update completed successfully.${NC}"