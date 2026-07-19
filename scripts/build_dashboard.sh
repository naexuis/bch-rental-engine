#!/usr/bin/env bash

###############################################################################
# BCH Rental Engine
# Build Dashboard
###############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}/config.sh"
source "${SCRIPT_DIR}/common.sh"
source "${SCRIPT_DIR}/docker_helper.sh"

print_banner "Build Dashboard"

cd "${PROJECT_DIR}"

#
# Docker Detection
#

initialize_docker

echo -e "${BLUE}Docker Command:${NC} ${DOCKER}"
echo -e "${BLUE}Image Name:${NC}     ${IMAGE_NAME}"
echo

echo "Building dashboard image..."

${DOCKER} build \
    -f "${DOCKERFILE}" \
    -t "${IMAGE_NAME}" \
    .

echo
echo -e "${GREEN}Dashboard image built successfully.${NC}"

echo
echo "Verifying image..."

${DOCKER} image inspect "${IMAGE_NAME}" >/dev/null

echo -e "${GREEN}Image verification successful.${NC}"