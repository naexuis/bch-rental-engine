# BCH Rental Engine - Umbrel Migration

## Status

- [x] Runtime configuration paths
    - BCH_CONFIG_DIR
    - BCH_STATE_DIR
    - BCH_LOG_DIR
    - POOLS_CONFIG_PATH
- [ ] Robust engine startup
- [ ] Dashboard deployment cleanup
- [ ] Shared Docker image
- [ ] Docker Compose
- [ ] Umbrel app manifest
- [ ] Umbrel app proxy
- [ ] Persistent app-data migration
- [ ] GitHub Container Registry images
- [ ] Umbrel installation documentation

---

## Phase 1 - Runtime

Goal:
Remove assumptions about filesystem layout.

Completed:
- Runtime config directory abstraction
- Configurable pools.json

Remaining:
- Robust run_engine.sh
- Optional .env handling
- Configurable polling interval

---

## Phase 2 - Containers

Goal:
Run the engine and dashboard from the same image.

Tasks:
- Single Dockerfile
- Multiple services
- Shared requirements
- Shared source tree

---

## Phase 3 - Umbrel

Goal:
Install with one click.

Tasks:
- docker-compose.yml
- umbrel-app.yml
- app_proxy
- APP_DATA_DIR volume
- Dashboard authentication

---

## Phase 4 - Release

Goal:
Publish publicly.

Tasks:
- GitHub Releases
- GHCR images
- Installation guide