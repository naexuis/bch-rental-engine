# BCH Rental Engine Release Checklist

This checklist is performed before every production release to ensure the BCH Rental Engine remains stable, reproducible, and fully documented.

---

# 1. Development Verification

## Working Tree

- [ ] Working tree is clean
- [ ] No uncommitted files
- [ ] No temporary debug code
- [ ] No commented-out production code

---

## Test-Driven Development

Every feature should have completed the full TDD cycle.

- [ ] Failing test written first
- [ ] Smallest production implementation completed
- [ ] Targeted test suite passes
- [ ] No unintended behavioral changes
- [ ] Commit created for each logical feature

---

## Code Quality

- [ ] Python compile passes

```bash
python -m py_compile scripts/*.py
```

- [ ] Linting (optional)
- [ ] No dead code introduced
- [ ] Logging reviewed
- [ ] Error handling verified

---

## Regression Testing

Run all project test suites.

- [ ] Trend tests
- [ ] Recommendation History tests
- [ ] Opportunity Score tests
- [ ] Dashboard tests (if applicable)
- [ ] Full regression suite passes

---

# 2. Documentation

Verify documentation reflects the release.

- [ ] README updated
- [ ] CHANGELOG updated
- [ ] ROADMAP updated
- [ ] ARCHITECTURE updated (if required)
- [ ] CONFIGURATION updated (if required)
- [ ] OPERATIONS updated (if required)
- [ ] RELEASE_CHECKLIST reviewed

---

# 3. Versioning

Update project version.

- [ ] Version number updated
- [ ] Release name updated
- [ ] Release notes written
- [ ] Breaking changes documented
- [ ] Migration notes written (if required)

---

# 4. Git

Verify repository state.

- [ ] Working tree clean

```bash
git status
```

- [ ] All feature commits completed
- [ ] Branch up to date
- [ ] Push to GitHub

```bash
git push
```

- [ ] Create release tag

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

---

# 5. Docker Build

Build production containers.

Engine

- [ ] Engine Docker image builds successfully

Dashboard

- [ ] Dashboard Docker image builds successfully

- [ ] No build warnings
- [ ] Image version correct

---

# 6. Umbrel Deployment

Deploy to production.

- [ ] Pull latest source
- [ ] Build dashboard
- [ ] Deploy dashboard
- [ ] Restart dashboard
- [ ] Engine configuration verified

Production helper scripts

```text
scripts/build_dashboard.sh
scripts/deploy_dashboard.sh
scripts/restart_dashboard.sh
scripts/check_dashboard.sh
scripts/update_dashboard.sh
```

---

# 7. Production Verification

Verify production environment.

- [ ] Dashboard accessible
- [ ] Health check passes
- [ ] Latest recommendation visible
- [ ] Recommendation History functioning
- [ ] Trend analytics displayed correctly
- [ ] Charts render correctly
- [ ] No console errors
- [ ] No container restart loops

---

# 8. Analytics Verification

Verify newly added analytics.

- [ ] Trend direction
- [ ] Confidence
- [ ] Persistence
- [ ] Velocity
- [ ] Volatility
- [ ] Trend strength
- [ ] Interpretation text
- [ ] Historical retrieval

---

# 9. Operational Verification

Confirm live engine operation.

- [ ] Market data downloads
- [ ] BCH difficulty updates
- [ ] Pool API functioning
- [ ] Rental pricing available
- [ ] SQLite history updated
- [ ] JSON state written
- [ ] JSONL logging functioning
- [ ] Telegram notifications working (if enabled)

---

# 10. Dashboard QA

Verify dashboard pages.

- [ ] Home
- [ ] Recommendation
- [ ] Recommendation History
- [ ] Charts
- [ ] Analytics
- [ ] Tables
- [ ] Mobile layout (if changed)

---

# 11. Release Archive

Store release artifacts.

- [ ] Git tag created
- [ ] CHANGELOG finalized
- [ ] Release notes archived
- [ ] Documentation committed
- [ ] Docker image version recorded

---

# Current Development Focus

## Completed

- ✅ Recommendation History
- ✅ Explainability
- ✅ Trend Intelligence
- ✅ Trend Confidence
- ✅ Trend Persistence
- ✅ Trend Velocity
- ✅ Trend Volatility
- ✅ Trend Strength
- ✅ Interpretation integration
- ✅ High-velocity trend promotion
- ✅ Comprehensive trend unit tests

---

## Active Development

Forecast Intelligence

Current priorities

- [ ] Trend acceleration
- [ ] Trend deceleration
- [ ] Trend reversal detection
- [ ] Plateau detection
- [ ] False trend detection
- [ ] Forecast confidence
- [ ] Early strike opportunity detection

---

# Release Approval

Development

- [ ] Approved

Testing

- [ ] Approved

Documentation

- [ ] Approved

Production

- [ ] Approved

Release Date

_____________________________

Version

_____________________________

Approved By

_____________________________