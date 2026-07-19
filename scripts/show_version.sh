#!/usr/bin/env bash

###############################################################################
# BCH Rental Engine
# Version Information
###############################################################################

set -e

PROJECT_NAME="BCH Rental Engine"

# Colors
GREEN="\033[0;32m"
BLUE="\033[0;34m"
NC="\033[0m"

echo
echo "=========================================================="
echo " ${PROJECT_NAME}"
echo "=========================================================="
echo

echo -e "${BLUE}Branch:${NC}      $(git branch --show-current)"
echo -e "${BLUE}Commit:${NC}      $(git rev-parse --short HEAD)"
echo -e "${BLUE}Tag:${NC}         $(git describe --tags --abbrev=0 2>/dev/null || echo "None")"

echo