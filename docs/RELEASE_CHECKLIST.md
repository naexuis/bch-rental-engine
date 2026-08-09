# BCH Rental Engine Release Checklist

This checklist is performed before every production release to ensure the BCH Rental Engine remains stable, reproducible, documented, and safe to deploy.

The release process follows the project engineering workflow:

```text
Design

↓

Unit Tests

↓

Implementation

↓

Compilation

↓

Runtime Validation

↓

Regression Testing

↓

Documentation

↓

Commit

↓

Push

↓

Release

↓

Deployment
```

---

# 1. Development Verification

## Working Tree

Verify the repository is ready for release.

- [ ] Working tree is clean
- [ ] No uncommitted files
- [ ] No untracked production files
- [ ] No temporary debug code
- [ ] No accidental test fixtures or scratch files
- [ ] No commented-out production code that should be removed
- [ ] Branch is the intended release branch

Verify:

```bash
git status
```

Expected:

```text
nothing to commit, working tree clean
```

---

## Test-Driven Development

Every logical feature should have completed the full TDD cycle.

- [ ] Expected behavior defined
- [ ] Failing test written first where applicable
- [ ] Smallest production implementation completed
- [ ] Targeted test passes
- [ ] Relevant subsystem tests pass
- [ ] No unintended behavioral changes introduced
- [ ] Full regression suite passes
- [ ] Commit created for each logical feature

For refactors where behavior already existed:

- [ ] Existing behavior protected by regression tests
- [ ] Refactor completed without changing the external contract
- [ ] Full regression suite remains green

---

# 2. Code Quality

## Python Compilation

Compile production Python modules.

```bash
python -m py_compile scripts/*.py
```

Compile storage modules:

```bash
python -m py_compile scripts/storage/*.py
```

Compile dashboard modules:

```bash
python -m py_compile dashboard/*.py
python -m py_compile dashboard/pages/*.py
python -m py_compile dashboard/components/*.py
python -m py_compile dashboard/charts/*.py
```

Verify:

- [ ] Engine compiles
- [ ] Storage subsystem compiles
- [ ] Dashboard compiles
- [ ] Dashboard pages compile
- [ ] Dashboard components compile
- [ ] No syntax errors

---

## Code Review

- [ ] No dead code introduced
- [ ] No duplicate production logic that should be shared
- [ ] Error handling reviewed
- [ ] Logging reviewed
- [ ] Configuration behavior reviewed
- [ ] File paths remain environment-independent
- [ ] No secrets or credentials are hardcoded
- [ ] Persistent files are written only to intended mounted directories

---

# 3. Regression Testing

Run the full project regression suite:

```bash
pytest -q
```

Verify:

- [ ] Full regression suite passes
- [ ] No skipped critical tests
- [ ] No unexpected warnings
- [ ] No flaky test behavior observed

Current release hardening includes coverage for:

- [ ] Recommendation logic
- [ ] Recommendation History
- [ ] Opportunity Score
- [ ] Trend Intelligence
- [ ] Interpretation
- [ ] Storage Manager
- [ ] History Manager
- [ ] Storage schema migrations
- [ ] Storage startup validation
- [ ] Storage retention
- [ ] Engine configuration
- [ ] Dashboard settings
- [ ] Dashboard utilities
- [ ] Dashboard decision mapping
- [ ] Frontier data
- [ ] Market utilities
- [ ] Yahoo Finance normalization
- [ ] Dashboard probability curves
- [ ] Storage/path behavior
- [ ] Engine launcher behavior

---

# 4. Storage & Reliability Verification

This section is required for Version 0.2 and later releases.

---

## Database Initialization

Verify a missing history database is created automatically.

- [ ] Parent state directory is created when necessary
- [ ] SQLite database is created
- [ ] `run_history` table is created
- [ ] Database starts at the current supported schema version

Expected database:

```text
state/bch_rental_history.sqlite
```

---

## Schema Versioning

Verify:

- [ ] `CURRENT_SCHEMA_VERSION` is correct
- [ ] Fresh database receives the current schema version
- [ ] Legacy databases upgrade successfully
- [ ] Existing history rows survive migration
- [ ] Sequential migration runner reaches the current version
- [ ] Database with a newer unsupported schema is rejected
- [ ] Migration notes are documented when required

Check manually if needed:

```bash
sqlite3 state/bch_rental_history.sqlite \
  "PRAGMA user_version;"
```

---

## Database Integrity

Verify SQLite integrity:

```bash
sqlite3 state/bch_rental_history.sqlite \
  "PRAGMA integrity_check;"
```

Expected:

```text
ok
```

Confirm:

- [ ] Integrity check passes
- [ ] Startup validation reports healthy storage
- [ ] Engine refuses normal startup if integrity validation fails

---

## Startup Validation

Verify storage validation occurs before normal engine execution.

- [ ] Database is initialized before engine work begins
- [ ] Schema migrations run before engine work begins
- [ ] Integrity check runs before engine work begins
- [ ] Failed storage validation stops engine execution
- [ ] Failure is written to operational logs/state as expected

---

## History Recording

Run the engine and confirm:

- [ ] One history row is written for each successful engine execution
- [ ] Latest history row contains expected recommendation fields
- [ ] Canonical decision is stored
- [ ] Opportunity Score is stored
- [ ] Opportunity Action is stored
- [ ] Budget configuration is stored
- [ ] History rows remain readable after schema migration

Inspect recent rows:

```bash
sqlite3 state/bch_rental_history.sqlite
```

```sql
SELECT
    id,
    timestamp,
    best_recommendation,
    opportunity_score,
    opportunity_action,
    canonical_decision
FROM run_history
ORDER BY id DESC
LIMIT 10;
```

---

## Storage Statistics

Verify the History Manager reports:

- [ ] Record count
- [ ] Oldest record timestamp
- [ ] Newest record timestamp
- [ ] Current database size

Verify values match the actual SQLite database.

---

## History Retention

Verify the configured history limit is respected.

Default:

```text
1073741824 bytes
```

Equivalent to:

```text
1 GiB
```

Confirm:

- [ ] Default maximum is 1 GiB
- [ ] User can increase the limit
- [ ] User can decrease the limit
- [ ] `0` disables size-based pruning
- [ ] Oldest rows are pruned first
- [ ] Newest rows are preserved
- [ ] Retention stops safely when no rows remain
- [ ] Retention does not loop indefinitely on impossible limits
- [ ] Database is compacted after automatic pruning

Configuration:

```text
BCH_HISTORY_MAX_SIZE_BYTES
```

Dashboard override key:

```text
history_max_size_bytes
```

---

## Unlimited History

Set:

```text
BCH_HISTORY_MAX_SIZE_BYTES=0
```

Verify:

- [ ] Engine accepts the configuration
- [ ] Automatic size pruning is disabled
- [ ] Dashboard displays `Unlimited`
- [ ] Operator understands disk growth must be monitored independently

Restore the intended production limit after testing if unlimited mode is not desired.

---

## Database Compaction

Verify:

- [ ] Automatic `VACUUM` works after pruning
- [ ] Manual Compact Database button works
- [ ] Database remains healthy after compaction
- [ ] Storage page refreshes after compaction
- [ ] Reclaimed space is reported correctly

---

# 5. Configuration Verification

Review runtime configuration behavior.

Configuration precedence for dashboard-supported values:

```text
Dashboard Override
        ↓
Environment Variable
        ↓
Built-in Default
```

Verify:

- [ ] Dashboard override file loads correctly
- [ ] Environment fallback works
- [ ] Invalid values fall back safely
- [ ] Dashboard changes persist
- [ ] Engine picks up dashboard changes on the next run
- [ ] Immediate-run trigger works after Settings changes
- [ ] Effective runtime values are written to state JSON

Review:

```text
config/dashboard_config_override.json
```

and:

```text
state/bch_solo_rental_strike_engine.json
```

Confirm the effective:

```text
config
```

object contains expected values.

---

# 6. Documentation

Verify documentation reflects the release.

Required review:

- [ ] README updated
- [ ] CHANGELOG updated
- [ ] ROADMAP updated
- [ ] RELEASE_CHECKLIST updated
- [ ] CONFIGURATION updated
- [ ] OPERATIONS updated
- [ ] ARCHITECTURE updated if architecture changed
- [ ] INSTALL updated if installation steps changed
- [ ] UMBREL_RELEASE_PROCESS reviewed
- [ ] Migration notes written if required

For Version 0.2 specifically, documentation should cover:

- [ ] Storage Manager
- [ ] History Manager
- [ ] Schema versioning
- [ ] Schema migration behavior
- [ ] Startup storage validation
- [ ] History retention
- [ ] 1 GiB default limit
- [ ] Unlimited history mode
- [ ] Storage dashboard
- [ ] Manual database compaction
- [ ] Effective runtime configuration

---

# 7. Versioning

Update project version before release.

- [ ] Version number updated
- [ ] Release name updated
- [ ] Version references are consistent across documentation
- [ ] Release notes written
- [ ] Breaking changes documented
- [ ] Database migration notes documented
- [ ] Upgrade instructions documented if required

Release version:

```text
vX.Y.Z
```

---

# 8. Git Verification

Verify repository state:

```bash
git status
```

Confirm:

- [ ] Working tree clean
- [ ] No untracked release files
- [ ] All feature commits completed
- [ ] Documentation commits completed
- [ ] Branch is up to date with origin

Push:

```bash
git push
```

Verify recent commits:

```bash
git --no-pager log --oneline -20
```

---

# 9. Release Tag

After all verification passes:

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

Confirm:

- [ ] Tag points to intended release commit
- [ ] Tag exists on GitHub
- [ ] Release notes match tagged code
- [ ] No commits are missing from the release

---

# 10. Docker Build

Build production containers.

## Engine

- [ ] Engine image builds successfully
- [ ] No dependency errors
- [ ] Entrypoint is correct
- [ ] Persistent paths are correct
- [ ] Engine starts successfully

## Dashboard

- [ ] Dashboard image builds successfully
- [ ] No dependency errors
- [ ] Dashboard starts successfully
- [ ] Health endpoint/check succeeds

Confirm:

- [ ] No unexpected build warnings
- [ ] Image version is correct
- [ ] Images contain the intended release commit

---

# 11. Umbrel Deployment

Deploy to the production Umbrel environment.

Before deployment:

- [ ] Production repository working tree is clean
- [ ] Current database is backed up
- [ ] Current configuration is backed up
- [ ] Persistent state directory is verified
- [ ] Release branch/tag is available remotely

Pull latest release source.

Build and deploy using the repository helper scripts where applicable.

Production helper scripts may include:

```text
scripts/build_dashboard.sh
scripts/deploy_dashboard.sh
scripts/restart_dashboard.sh
scripts/check_dashboard.sh
scripts/update_dashboard.sh
```

Confirm:

- [ ] Source pulled successfully
- [ ] Engine image built
- [ ] Dashboard image built
- [ ] Containers replaced successfully
- [ ] Persistent volumes remain mounted
- [ ] Configuration survives deployment
- [ ] SQLite history survives deployment
- [ ] Dashboard becomes available

---

# 12. Production Storage Verification

Immediately after deployment:

- [ ] Existing SQLite history still exists
- [ ] Database schema migration succeeds if required
- [ ] `PRAGMA user_version` matches the release schema
- [ ] Integrity check passes
- [ ] Record count is reasonable
- [ ] Oldest record remains present as expected
- [ ] Newest record updates after an engine run
- [ ] Configured retention limit is correct
- [ ] Storage page reports healthy status
- [ ] Storage page database size matches the actual database
- [ ] Storage page configured maximum matches effective runtime config
- [ ] Compact Database control works

Do not continue normal operation if database integrity fails.

---

# 13. Production Engine Verification

Confirm live engine operation.

- [ ] Engine starts without errors
- [ ] Startup storage validation passes
- [ ] Market data downloads
- [ ] BCH difficulty updates
- [ ] Network hashrate is available
- [ ] Braiins pricing is available or override works
- [ ] MiningRigRentals pricing works when enabled
- [ ] Pool routing executes
- [ ] Strike optimization executes
- [ ] Recommendation generated
- [ ] Canonical decision generated
- [ ] SQLite history updated
- [ ] JSON state written
- [ ] JSONL logging functioning
- [ ] Telegram notifications working if enabled
- [ ] No restart loop occurs

---

# 14. Dashboard QA

Verify every current dashboard page.

- [ ] Dashboard
- [ ] Market
- [ ] Market Trends
- [ ] Strike Analysis
- [ ] Pool Routing
- [ ] History
- [ ] Storage
- [ ] Settings

Verify:

- [ ] Navigation works
- [ ] Auto refresh works
- [ ] Manual refresh works
- [ ] Latest recommendation visible
- [ ] Recommendation state renders correctly
- [ ] Waiting state renders correctly
- [ ] Charts render correctly
- [ ] Tables render correctly
- [ ] No Streamlit exceptions
- [ ] No browser console errors that affect operation
- [ ] No container restart loops

---

# 15. Storage Dashboard QA

Verify the Storage page specifically.

- [ ] Current database size displayed
- [ ] Retention limit displayed
- [ ] Unlimited mode displayed correctly when enabled
- [ ] Storage utilization displayed
- [ ] History record count displayed
- [ ] Oldest record displayed
- [ ] Newest record displayed
- [ ] Database health displayed
- [ ] Integrity status displayed
- [ ] Compact Database button works
- [ ] Compaction result is reported
- [ ] Page reflects effective runtime configuration

---

# 16. Settings Dashboard QA

Verify Settings page behavior.

- [ ] Budget minimum editable
- [ ] Budget maximum editable
- [ ] Budget step editable
- [ ] Hashrate minimum editable
- [ ] Hashrate maximum editable
- [ ] Hashrate step editable
- [ ] History retention displayed
- [ ] History retention editable in GiB
- [ ] `0` represents unlimited history
- [ ] Save validation works
- [ ] Override JSON updated
- [ ] Immediate engine run requested after save
- [ ] New effective values appear after engine execution

---

# 17. Analytics Verification

Verify analytics remain correct after the release.

- [ ] Opportunity Score
- [ ] Recommendation reasoning
- [ ] Trend direction
- [ ] Trend confidence
- [ ] Trend persistence
- [ ] Trend velocity
- [ ] Trend volatility
- [ ] Trend strength
- [ ] Interpretation text
- [ ] Historical retrieval
- [ ] Historical trend windows

No storage change should alter the decision model unless explicitly documented.

---

# 18. Operational Verification

Verify normal operational behavior over multiple engine cycles.

- [ ] Engine executes repeatedly
- [ ] History record count increases
- [ ] Storage statistics update
- [ ] Latest state updates
- [ ] Dashboard refreshes
- [ ] Trend analytics continue accumulating history
- [ ] Retention does not prune while below the configured limit
- [ ] Logs remain healthy
- [ ] No unexpected disk growth
- [ ] No unexpected CPU or memory growth

---

# 19. Backup and Recovery Verification

Before production release:

- [ ] Back up `config/`
- [ ] Back up `state/`
- [ ] Back up SQLite Recommendation History

Highest priority:

```text
state/bch_rental_history.sqlite
```

Verify recovery procedure:

- [ ] Backup can be restored
- [ ] Restored database passes integrity check
- [ ] Restored database schema is supported
- [ ] Engine starts successfully against restored history

---

# 20. Release Archive

Store release artifacts and metadata.

- [ ] Git tag created
- [ ] CHANGELOG finalized
- [ ] Release notes archived
- [ ] Documentation committed
- [ ] Docker image version recorded
- [ ] Release commit recorded
- [ ] Schema version recorded
- [ ] Production deployment date recorded

---

# Current Release Status

## Version 0.2 — Storage & Reliability

Status:

```text
Production Validated
```

### Completed

- ✅ Self-initializing SQLite history database
- ✅ Automatic database creation
- ✅ Explicit schema versioning
- ✅ Sequential schema migration runner
- ✅ Legacy schema upgrade support
- ✅ Unsupported future-schema protection
- ✅ SQLite integrity checks
- ✅ Startup storage validation
- ✅ Recommendation History recording
- ✅ History storage statistics
- ✅ Automatic oldest-row pruning
- ✅ Maximum database size retention
- ✅ 1 GiB default history limit
- ✅ Unlimited-history mode
- ✅ Automatic SQLite compaction after pruning
- ✅ Operator-configurable history retention
- ✅ Engine configuration manager
- ✅ Effective runtime configuration published in state
- ✅ Storage dashboard
- ✅ Database health display
- ✅ Manual Compact Database control
- ✅ Modular dashboard page architecture
- ✅ Expanded storage and dashboard regression tests

### Remaining Release Closeout

- [x] Final documentation review
- [x] CHANGELOG update
- [x] ROADMAP update
- [x] ARCHITECTURE review/update
- [x] OPERATIONS review — no release change required
- [x] README review/update
- [x] Final post-documentation compile verification
- [x] Final post-documentation full regression verification
- [x] Local runtime validation
- [x] Docker image build and runtime verification
- [x] Umbrel production deployment validation
- [x] Production storage and history verification
- [x] Release version promoted to v0.2.0
- [x] Release notes prepared
- [ ] Create and push Git tag `v0.2.0`

---

# Next Development Milestone

## Version 0.3 — System Intelligence

Planned focus after Version 0.2 is released:

- Engine Health
- API Health
- Pricing Source Status
- Rental Source Status
- Database Health
- Startup Diagnostics
- Automatic Recovery
- Background Task Monitoring
- Self-test Framework

Forecast Intelligence remains planned for Version 0.4.

---

# Release Approval

## Development

- [ ] Approved

## Testing

- [ ] Approved

## Documentation

- [ ] Approved

## Production

- [ ] Approved

Release Date:

```text
_____________________________
```

Version:

```text
_____________________________
```

Approved By:

```text
_____________________________
```