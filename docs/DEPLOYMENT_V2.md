# Deployment & Operations (v2.1)

## Goal

Provide a simple, reliable deployment workflow for the BCH Rental Engine.

Deployment should require a single command and automatically verify that the dashboard is healthy.

---

# Objectives

- Reduce manual deployment steps.
- Standardize deployment.
- Improve operational reliability.
- Provide health verification.
- Display build/version information.
- Simplify future releases.

---

# Scripts

deploy_dashboard.sh

Purpose:
Build and deploy a new dashboard image.

---

update_dashboard.sh

Purpose:
Pull the latest code, rebuild, and restart the dashboard.

---

restart_dashboard.sh

Purpose:
Restart the dashboard without rebuilding.

---

check_dashboard.sh

Purpose:
Verify:

• Container running
• Port available
• Dashboard responding
• Version information

---

backup_state.sh

Purpose:

Backup:

config/

state/

SQLite database

before upgrades.

---

# Dashboard Metadata

Display:

Version

Git Commit

Build Date

Container Status

Last Engine Run

---

# Success Criteria

Deployment requires one command.

Deployment automatically verifies success.

Dashboard displays build information.

No manual Docker commands required during normal updates.