#!/usr/bin/env bash

###############################################################################
# BCH Rental Engine
# Operations Configuration
###############################################################################

# This file is sourced by the operational scripts.
# Every setting may be overridden with an environment variable.

CONFIG_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${BCH_PROJECT_DIR:-$(cd "${CONFIG_SCRIPT_DIR}/.." && pwd)}"

# ---------------------------------------------------------------------------
# Docker resources
# ---------------------------------------------------------------------------

IMAGE_NAME="${BCH_DASHBOARD_IMAGE:-bch-rental-dashboard}"
CONTAINER_NAME="${BCH_DASHBOARD_CONTAINER:-bch-rental-dashboard}"
DOCKERFILE="${BCH_DOCKERFILE:-Dockerfile.dashboard}"

# ---------------------------------------------------------------------------
# Dashboard network settings
# ---------------------------------------------------------------------------

DASHBOARD_HOST="${BCH_DASHBOARD_HOST:-0.0.0.0}"
DASHBOARD_PORT="${BCH_DASHBOARD_PORT:-8501}"
DASHBOARD_URL="${BCH_DASHBOARD_URL:-http://localhost:${DASHBOARD_PORT}}"

# ---------------------------------------------------------------------------
# Persistent host directories
# ---------------------------------------------------------------------------

HOST_STATE_DIR="${BCH_HOST_STATE_DIR:-${PROJECT_DIR}/state}"
HOST_CONFIG_DIR="${BCH_HOST_CONFIG_DIR:-${PROJECT_DIR}/config}"

# ---------------------------------------------------------------------------
# Paths presented inside the dashboard container
# ---------------------------------------------------------------------------

CONTAINER_STATE_DIR="${BCH_CONTAINER_STATE_DIR:-/root/bch_rental_engine/state}"
CONTAINER_CONFIG_DIR="${BCH_CONTAINER_CONFIG_DIR:-/root/bch_rental_engine/config}"