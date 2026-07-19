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