#!/usr/bin/env bash

###############################################################################
# BCH Rental Engine
# Dashboard Health Check
###############################################################################

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

CONTAINER_NAME="${BCH_DASHBOARD_CONTAINER:-bch-rental-dashboard}"
DASHBOARD_URL="${BCH_DASHBOARD_URL:-http://localhost:8501}"

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m"

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

pass() {
    echo -e "${GREEN}PASS${NC}  $1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

fail() {
    echo -e "${RED}FAIL${NC}  $1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

warn() {
    echo -e "${YELLOW}WARN${NC}  $1"
    WARN_COUNT=$((WARN_COUNT + 1))
}

echo
echo "=========================================================="
echo " BCH Rental Engine Dashboard Health Check"
echo "=========================================================="
echo

cd "${PROJECT_DIR}" || exit 1

"${SCRIPT_DIR}/show_version.sh"

echo -e "${BLUE}Dashboard checks${NC}"
echo

if ! command -v docker >/dev/null 2>&1; then
    fail "Docker is not installed or is not available in PATH."
else
    pass "Docker command is available."

    if docker inspect "${CONTAINER_NAME}" >/dev/null 2>&1; then
        pass "Container '${CONTAINER_NAME}' exists."

        CONTAINER_STATUS="$(
            docker inspect \
                --format '{{.State.Status}}' \
                "${CONTAINER_NAME}" \
                2>/dev/null
        )"

        if [[ "${CONTAINER_STATUS}" == "running" ]]; then
            pass "Container '${CONTAINER_NAME}' is running."
        else
            fail "Container '${CONTAINER_NAME}' status is '${CONTAINER_STATUS}'."
        fi
    else
        fail "Container '${CONTAINER_NAME}' does not exist."
    fi
fi

if ! command -v curl >/dev/null 2>&1; then
    warn "curl is not installed; dashboard HTTP check was skipped."
else
    HTTP_STATUS="$(
        curl \
            --silent \
            --show-error \
            --output /dev/null \
            --write-out '%{http_code}' \
            --max-time 10 \
            "${DASHBOARD_URL}" \
            2>/dev/null || true
    )"

    if [[ "${HTTP_STATUS}" =~ ^2|3 ]]; then
        pass "Dashboard responded at ${DASHBOARD_URL} with HTTP ${HTTP_STATUS}."
    else
        fail "Dashboard did not respond successfully at ${DASHBOARD_URL}."
    fi
fi

echo
echo "----------------------------------------------------------"
echo " Results"
echo "----------------------------------------------------------"
echo -e "${GREEN}Passed:${NC}   ${PASS_COUNT}"
echo -e "${YELLOW}Warnings:${NC} ${WARN_COUNT}"
echo -e "${RED}Failed:${NC}   ${FAIL_COUNT}"
echo

if (( FAIL_COUNT > 0 )); then
    echo -e "${RED}Dashboard health check failed.${NC}"
    exit 1
fi

echo -e "${GREEN}Dashboard health check passed.${NC}"
exit 0