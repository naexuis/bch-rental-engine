#!/usr/bin/env bash

###############################################################################
# BCH Rental Engine
# Version Information
###############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "${SCRIPT_DIR}/config.sh"
source "${SCRIPT_DIR}/common.sh"

SHOW_BANNER=true

if [[ "${1:-}" == "--no-banner" ]]; then
    SHOW_BANNER=false
fi

cd "${PROJECT_DIR}"

if [[ "${SHOW_BANNER}" == true ]]; then
    print_banner "Version Information"
else
    echo -e "${BLUE}Version information${NC}"
    echo
fi

BRANCH="$(git branch --show-current 2>/dev/null || true)"
COMMIT="$(git rev-parse --short HEAD 2>/dev/null || echo "Unknown")"
EXACT_TAG="$(git tag --points-at HEAD 2>/dev/null | head -n 1 || true)"
LATEST_TAG="$(git describe --tags --abbrev=0 HEAD 2>/dev/null || true)"

if [[ -n "${LATEST_TAG}" ]]; then
    COMMITS_AHEAD="$(git rev-list --count "${LATEST_TAG}..HEAD" 2>/dev/null || echo "Unknown")"
else
    COMMITS_AHEAD="Unknown"
fi

if [[ -n "${EXACT_TAG}" ]]; then
    VERSION="${EXACT_TAG}"
elif [[ -n "${LATEST_TAG}" ]]; then
    VERSION="${LATEST_TAG}+${COMMITS_AHEAD}"
else
    VERSION="Unreleased"
fi

printf '%-18s %s\n' "Version:" "${VERSION}"
printf '%-18s %s\n' "Branch:" "${BRANCH:-Detached HEAD}"
printf '%-18s %s\n' "Current Commit:" "${COMMIT}"
printf '%-18s %s\n' "Latest Release:" "${LATEST_TAG:-None}"
printf '%-18s %s\n' "Commits Ahead:" "${COMMITS_AHEAD}"
echo