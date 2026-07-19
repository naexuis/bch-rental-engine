#!/usr/bin/env bash

###############################################################################
# BCH Rental Engine
# Deploy Dashboard
###############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}/config.sh"
source "${SCRIPT_DIR}/common.sh"
source "${SCRIPT_DIR}/docker_helper.sh"

print_banner "Deploy Dashboard"

cd "${PROJECT_DIR}"

initialize_docker

echo -e "${BLUE}Docker Command:${NC} ${DOCKER}"
echo -e "${BLUE}Image Name:${NC}     ${IMAGE_NAME}"
echo -e "${BLUE}Container:${NC}      ${CONTAINER_NAME}"
echo -e "${BLUE}Dashboard URL:${NC}  ${DASHBOARD_URL}"
echo

if ! ${DOCKER} image inspect "${IMAGE_NAME}" >/dev/null 2>&1; then
    echo -e "${RED}ERROR:${NC} Docker image '${IMAGE_NAME}' does not exist."
    echo "Run ./scripts/build_dashboard.sh first."
    exit 1
fi

mkdir -p "${HOST_STATE_DIR}"
mkdir -p "${HOST_CONFIG_DIR}"

if ${DOCKER} inspect "${CONTAINER_NAME}" >/dev/null 2>&1; then
    echo "Stopping existing dashboard container..."
    ${DOCKER} stop "${CONTAINER_NAME}" >/dev/null || true

    echo "Removing existing dashboard container..."
    ${DOCKER} rm "${CONTAINER_NAME}" >/dev/null
fi

echo "Starting dashboard container..."

${DOCKER} run -d \
    --name "${CONTAINER_NAME}" \
    --restart unless-stopped \
    -p "${DASHBOARD_PORT}:8501" \
    -e BCH_STATE_DIR="${CONTAINER_STATE_DIR}" \
    -e BCH_CONFIG_DIR="${CONTAINER_CONFIG_DIR}" \
    -v "${HOST_STATE_DIR}:${CONTAINER_STATE_DIR}" \
    -v "${HOST_CONFIG_DIR}:${CONTAINER_CONFIG_DIR}" \
    "${IMAGE_NAME}" \
    >/dev/null

echo -e "${GREEN}Dashboard container started.${NC}"
echo
echo "Waiting for dashboard availability..."

DASHBOARD_READY=false

for attempt in {1..15}; do
    if curl \
        --silent \
        --fail \
        --max-time 5 \
        "${DASHBOARD_URL}" \
        >/dev/null 2>&1; then

        DASHBOARD_READY=true
        break
    fi

    echo "Health check attempt ${attempt}/15..."
    sleep 2
done

echo

if [[ "${DASHBOARD_READY}" != true ]]; then
    echo -e "${RED}ERROR:${NC} Dashboard did not become reachable."
    echo
    echo "Recent container logs:"
    ${DOCKER} logs --tail 50 "${CONTAINER_NAME}" || true
    exit 1
fi

echo -e "${GREEN}Dashboard is responding successfully.${NC}"
echo

"${SCRIPT_DIR}/check_dashboard.sh"