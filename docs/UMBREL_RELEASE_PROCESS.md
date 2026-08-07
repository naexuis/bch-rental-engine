# BCH Rental Engine
# Umbrel Release Process

**Document Version:** 2.0

**Last Updated:** 2026-08-06

---

# Purpose

This document describes the complete production release workflow for the BCH Rental Engine.

The objective is to make every release:

- Repeatable
- Versioned
- Fully tested
- Easy to rollback
- Consistent across GitHub, GHCR, and Umbrel

Following this process ensures that the source code, Docker images, and Umbrel App Store remain synchronized.

---

# Release Architecture

The BCH Rental Engine is deployed using **two Git repositories** and **GitHub Container Registry (GHCR)**.

```
Developer Workstation
        │
        ▼
┌──────────────────────────────┐
│ bch-rental-engine            │
│ Application Source Code      │
└──────────────────────────────┘
        │
        ▼
GitHub Repository
        │
        ▼
Production Umbrel Host
        │
        ▼
Build Production Docker Image
        │
        ▼
GitHub Container Registry (GHCR)
        │
        ▼
┌──────────────────────────────┐
│ umbrel-app-store             │
│ naexuis-bch-rental-engine    │
└──────────────────────────────┘
        │
        ▼
Umbrel App Store
        │
        ▼
Installed BCH Rental Engine
```

---

# Repository Overview

## 1. Application Repository

Location:

```text
~/projects/bch-rental-engine
```

Contains:

- Python source code
- Streamlit dashboard
- Dockerfiles
- Tests
- Documentation
- Configuration
- Release tags

This repository contains **the application itself**.

---

## 2. Umbrel App Store Repository

Location:

```text
~/projects/umbrel-app-store
```

Contains:

```text
naexuis-bch-rental-engine/

    docker-compose.yml
    umbrel-app.yml
```

This repository tells Umbrel:

- which Docker image to download
- which image tag to install
- application metadata
- application version

---

# Important Architecture Note

The application repository is **not** what Umbrel installs.

Umbrel installs the Docker image referenced by the Umbrel App Store repository.

Every production release therefore follows this pipeline:

```
Application Code

↓

Production Docker Image

↓

GitHub Container Registry (GHCR)

↓

Umbrel App Store

↓

Umbrel Installation
```

---

# Release Checklist

Before releasing verify:

## Development

- [ ] Working tree clean
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Feature committed
- [ ] GitHub pushed
- [ ] Release tag created (if applicable)

---

## Docker

- [ ] Production image built
- [ ] Image tagged correctly
- [ ] Image pushed to GHCR

---

## Umbrel App Store

- [ ] Version updated
- [ ] Docker image tag updated
- [ ] Changes committed
- [ ] Changes pushed

---

## Production QA

- [ ] Engine starts
- [ ] Dashboard loads
- [ ] BCH price updates
- [ ] Braiins pricing loads
- [ ] MiningRigRentals pricing loads
- [ ] Strike scenarios generated
- [ ] Canonical decision generated
- [ ] State file updated
- [ ] History database updated
- [ ] No container errors

---

# STEP 1 — Finish Development

Inside:

```text
~/projects/bch-rental-engine
```

Verify the repository is clean.

```bash
git status
```

Expected:

```text
working tree clean
```

Run the full regression suite.

```bash
pytest -q
```

Expected:

```text
All tests pass
```

Commit any remaining changes.

```bash
git add .
git commit -m "<release message>"
git push
```

Optionally create a release tag.

Example:

```bash
git tag recommendation-engine-v2
git push origin recommendation-engine-v2
```

---

# STEP 2 — Pull onto the Production Umbrel Host

SSH into Umbrel.

```bash
ssh umbrel@<umbrel-ip>
```

Go to the project.

```bash
cd ~/bch_rental_engine
```

Pull the latest code.

```bash
git pull origin feature/umbrel-native-app
```

Verify.

```bash
git status
```

Expected:

```text
working tree clean
```

---

# STEP 3 — Build the Production Docker Image

**Important**

Production Docker images are built on the Umbrel server.

Do **not** build production images inside the development container.

Example:

```bash
docker build \
    --no-cache \
    -t ghcr.io/naexuis/bch-rental-engine:0.1.4 \
    .
```

Verify:

```bash
docker images
```

Confirm the correct image exists.

---

# STEP 4 — Authenticate with GHCR

If necessary:

```bash
docker login ghcr.io
```

Authenticate using:

- GitHub username
- GitHub Personal Access Token

Never use your GitHub password.

---

# STEP 5 — Push the Docker Image

Example:

```bash
docker push ghcr.io/naexuis/bch-rental-engine:0.1.4
```

Verify that the push completes successfully.

The new image should now be available in GitHub Container Registry.

---

# STEP 6 — Update the Umbrel App Store Repository

Open:

```text
~/projects/umbrel-app-store
```

Navigate to:

```text
naexuis-bch-rental-engine/
```

Two files normally require updates:

```text
docker-compose.yml

umbrel-app.yml
```

---

## Update the Application Version

Example:

```text
0.1.3

↓

0.1.4
```

Update the version inside:

```text
umbrel-app.yml
```

---

## Update the Docker Image Tag

Update every image reference.

Example:

```text
ghcr.io/naexuis/bch-rental-engine:0.1.3

↓

ghcr.io/naexuis/bch-rental-engine:0.1.4
```

Usually this occurs in:

```text
docker-compose.yml
```

---

Commit the App Store changes.

```bash
git add .
git commit -m "Release BCH Rental Engine v0.1.4"
git push
```

---

# STEP 7 — Upgrade the Umbrel App

Open the Umbrel dashboard.

Navigate to:

```text
App Store

↓

BCH Rental Engine
```

Select:

```text
Upgrade
```

Umbrel will:

- download the new Docker image
- recreate the containers
- restart the application

---

# STEP 8 — Verify Containers

Verify the containers are running.

```bash
docker ps
```

Inspect logs.

```bash
docker logs -f <container_name>
```

Look for:

- Python exceptions
- Missing environment variables
- Missing mounts
- Permission errors
- Configuration problems

---

# STEP 9 — Dashboard QA

Open:

```text
http://<umbrel-ip>:8501
```

Verify:

- Dashboard loads
- Decision Center renders
- Canonical Decision displays correctly
- Opportunity Score updates
- Recommendation updates
- Market data refreshes

---

# STEP 10 — Engine QA

Verify that the engine is functioning correctly.

Confirm:

- BCH price updates
- Braiins pricing updates
- MiningRigRentals pricing updates
- Strike scenarios generated
- Canonical Decision generated
- Recommendation generated
- SQLite history updated
- JSON state updated
- Dashboard refreshed

A successful QA completes the release.

---

# Rollback Procedure

If a release must be reverted:

1. Update the Umbrel App Store image tag back to the previous release.

Example:

```text
0.1.4

↓

0.1.3
```

2. Commit the App Store repository.

```bash
git add .
git commit -m "Rollback BCH Rental Engine to v0.1.3"
git push
```

3. Upgrade the application again from Umbrel.

Since the previous Docker image already exists in GHCR, Umbrel will reinstall the earlier version.

---

# Versioning Guidelines

Use Semantic Versioning.

Examples:

```
0.1.3 → 0.1.4

Bug fixes
Minor improvements
Documentation
```

```
0.1.4 → 0.2.0

Major feature release
New subsystem
Architecture improvements
```

```
0.9.x → 1.0.0

First production-ready stable release
```

---

# Common Problems

## GHCR Authentication Failure

```bash
docker login ghcr.io
```

Use a GitHub Personal Access Token.

---

## Wrong Docker Image

Verify:

```bash
docker images
```

Ensure the expected tag exists.

---

## Umbrel Still Running an Older Version

Verify:

- Docker image tag was updated
- App Store repository was pushed
- Umbrel upgrade completed successfully

---

## Wrong Version Displayed

Both repositories must be updated.

Application Repository:

```text
bch-rental-engine
```

Umbrel Repository:

```text
umbrel-app-store
```

---

## Dashboard Does Not Reflect New Changes

Possible causes:

- old Docker image
- cached image
- incorrect Docker tag
- App Store repository not updated
- Umbrel upgrade not completed

---

## Engine Will Not Start

Inspect:

```bash
docker logs
```

Common causes:

- syntax errors
- missing configuration
- missing volume mounts
- missing environment variables

---

# Release Workflow Summary

```
Write Code
      │
      ▼
Run Tests
      │
      ▼
Commit
      │
      ▼
Push GitHub
      │
      ▼
(Optional) Create Git Tag
      │
      ▼
Pull on Umbrel
      │
      ▼
Build Docker Image
      │
      ▼
Push Image to GHCR
      │
      ▼
Update Umbrel App Store
      │
      ▼
Commit
      │
      ▼
Push
      │
      ▼
Upgrade App
      │
      ▼
Production QA
```

---

# Release Philosophy

Every production release should satisfy the following principles.

- Every release is reproducible.
- Every release has a unique Docker image tag.
- Every release is backed by a Git commit.
- Every release passes the automated test suite.
- Every release can be rolled back.
- The Application Repository and Umbrel App Store Repository remain synchronized.
- Documentation is updated alongside the code.

Following this document should allow future releases to be completed in only a few minutes while maintaining a reliable and repeatable deployment process.