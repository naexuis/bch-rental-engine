# BCH Rental Engine Scripts

This directory contains operational scripts used to deploy, maintain, and monitor the BCH Rental Engine.

---

## deploy_dashboard.sh

Builds a new Docker image and deploys the dashboard.

---

## update_dashboard.sh

Pulls the latest code from GitHub and deploys the newest version.

---

## restart_dashboard.sh

Restarts the dashboard container without rebuilding.

---

## check_dashboard.sh

Performs a health check of the running dashboard.

Checks include:

- Docker container
- Port availability
- Dashboard status

---

## show_version.sh

Displays version and deployment information.

---

## backup_state.sh

Creates a backup of:

- config/
- state/
- SQLite database

before upgrades.