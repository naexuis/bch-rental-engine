#!/usr/bin/env bash

###############################################################################
# BCH Rental Engine
# Docker Helper
###############################################################################

DOCKER=""
DOCKER_AVAILABLE=false

detect_docker() {
    if docker ps >/dev/null 2>&1; then
        DOCKER="docker"
        DOCKER_AVAILABLE=true
        return
    fi

    if sudo -n docker ps >/dev/null 2>&1; then
        DOCKER="sudo docker"
        DOCKER_AVAILABLE=true
        return
    fi

    DOCKER=""
    DOCKER_AVAILABLE=false
}

initialize_docker() {
    detect_docker

    if [[ "${DOCKER_AVAILABLE}" == true ]]; then
        return
    fi

    if command -v sudo >/dev/null 2>&1; then
        echo -e "${YELLOW}Docker requires elevated privileges.${NC}"
        echo "Please enter your password if prompted."
        echo

        if sudo -v; then
            detect_docker
        fi
    fi

    if [[ "${DOCKER_AVAILABLE}" != true ]]; then
        echo -e "${RED}ERROR:${NC} Docker is not available."
        echo "Confirm Docker is installed and that your user has permission to use it."
        exit 1
    fi
}