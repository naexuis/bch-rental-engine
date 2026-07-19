#!/usr/bin/env bash

###############################################################################
# BCH Rental Engine
# Restart Dashboard
###############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}/config.sh"
source "${SCRIPT_DIR}/common.sh"
source "${SCRIPT_DIR}/docker_helper.sh"

print_banner "Restart Dashboard"

cd "${PROJECT_DIR}"

initialize_docker

echo -e "${BLUE}Docker command:${NC} ${DOCKER}"
echo -e "${BLUE}Container:${NC}      ${CONTAINER_NAME}"
echo

if ! ${DOCKER} inspect "${CONTAINER_NAME}" >/dev/null 2>&1; then
    echo -e "${RED}ERROR:${NC} Container '${CONTAINER_NAME}' does not exist."
    echo
    echo "Run the deployment script first once it has been implemented."
    exit 1
fi

echo "Restarting dashboard container..."

${DOCKER} restart "${CONTAINER_NAME}" >/dev/null

echo -e "${GREEN}Container restart command completed.${NC}"
echo
echo "Waiting for the dashboard to become available..."

DASHBOARD_READY=false

for attempt in {1..10}; do
    if curl \
        --silent \
        --fail \
        --max-time 5 \
        "${DASHBOARD_URL}" \
        >/dev/null 2>&1; then

        DASHBOARD_READY=true
        break
    fi

    echo "Health check attempt ${attempt}/10..."
    sleep 2
done

echo

if [[ "${DASHBOARD_READY}" != true ]]; then
    echo -e "${RED}ERROR:${NC} Dashboard did not become reachable at:"
    echo "${DASHBOARD_URL}"
    echo
    echo "Recent container logs:"
    ${DOCKER} logs --tail 30 "${CONTAINER_NAME}" || true
    exit 1
fi

echo -e "${GREEN}Dashboard is responding successfully.${NC}"
echo

"${SCRIPT_DIR}/check_dashboard.sh"