# BCH Rental Engine Operations Runbook

This runbook describes the day-to-day administration, monitoring, maintenance, deployment, and troubleshooting procedures for the BCH Rental Engine.

It is intended for operators responsible for keeping the production system healthy while maintaining strict separation between development and production environments.

---

# Operational Philosophy

The BCH Rental Engine is designed to operate continuously with minimal manual intervention.

Operational priorities are:

1. Preserve reliable engine execution.
2. Protect Recommendation History.
3. Detect storage or database problems early.
4. Prevent uncontrolled storage growth.
5. Keep production deployments reproducible.
6. Maintain clear separation between development and production.
7. Prefer built-in management workflows over manual intervention.

The application should be capable of running unattended for extended periods while providing enough visibility for an operator to understand its current state.

---

# Environment Separation

The BCH Rental Engine uses separate development and production environments.

## Development

Purpose:

- Feature development
- Test-Driven Development (TDD)
- Unit testing
- Integration testing
- Documentation updates
- Experimental work

Default location:

```text
~/projects/bch-rental-engine
```

Characteristics:

- Frequent commits
- Feature branches
- May contain unfinished work
- Safe to modify
- Used for testing before deployment
- Never serves production traffic

Development work should remain isolated from production.

---

## Production

Purpose:

- Stable engine execution
- Dashboard hosting
- Recommendation generation
- Historical data collection
- Operator access

Default location:

```text
~/bch_rental_engine
```

Characteristics:

- Dockerized application components
- Persistent configuration
- Persistent SQLite history
- Persistent logs
- Stable releases only
- Working tree should remain clean
- Updated only through the deployment workflow

Development should never be performed directly in the production repository.

---

# Standard Release Workflow

Every production release should follow the same sequence.

```text
Development
    ↓
TDD Complete
    ↓
Targeted Tests
    ↓
Full Regression Tests
    ↓
Documentation Updated
    ↓
Git Commit
    ↓
Git Push
    ↓
Release Tag
    ↓
Umbrel Update
    ↓
Startup Validation
    ↓
Health Check
    ↓
Production Verification
```

Only tested and documented releases should be deployed to production.

Refer to:

```text
docs/RELEASE_CHECKLIST.md
```

for the complete release procedure.

---

# Standard Umbrel Update Workflow

The preferred production update method is:

```bash
cd ~/bch_rental_engine

./scripts/update_dashboard.sh
```

The update workflow is designed to:

1. Verify the production working tree is clean.
2. Fetch the latest Git commits and tags.
3. Perform a fast-forward-only update.
4. Build the dashboard image.
5. Replace the running dashboard container.
6. Wait for the dashboard to become available.
7. Execute the dashboard health check.

Manual Docker commands should normally be unnecessary.

---

# Repository Layout

## Development

```text
~/projects/bch-rental-engine
```

## Production

```text
~/bch_rental_engine
```

Important directories:

```text
config/
dashboard/
docs/
logs/
scripts/
state/
tests/
```

Important persistent files:

```text
config/.env
config/dashboard_config_override.json
config/pools.json

state/bch_solo_rental_strike_engine.json
state/bch_rental_history.sqlite

logs/bch_solo_rental_strike_engine.jsonl
logs/bch_solo_rental_strike_engine_alerts.jsonl
```

The `config/`, `state/`, and `logs/` directories contain operational data and should be treated differently from replaceable application code.

---

# Persistent Data

The most important persistent application data is:

```text
state/bch_rental_history.sqlite
```

This SQLite database contains Recommendation History and supports:

- Historical recommendations
- Opportunity Score history
- Trend Intelligence
- Historical comparisons
- Operator analysis
- Future replay capabilities
- Future historical intelligence

The database should be considered a production asset.

Application code can be restored from Git.

Historical observations cannot be recreated if they were never preserved.

---

# Engine Execution

## Recommended Execution

The engine should normally run through the application's production launcher.

For manual development or diagnostic execution, use the module form:

```bash
python -m scripts.bch_solo_rental_strike_engine
```

This is preferred over:

```bash
python scripts/bch_solo_rental_strike_engine.py
```

because the application is structured as a Python package.

---

# Loading Environment Variables

When running manually outside the production launcher:

```bash
set -a
source config/.env
set +a
```

Then run:

```bash
python -m scripts.bch_solo_rental_strike_engine
```

---

# Successful Engine Run

A successful engine execution should:

1. Validate storage.
2. Retrieve current market data.
3. Evaluate rental scenarios.
4. Generate a recommendation.
5. Calculate Opportunity Score.
6. Calculate trend intelligence.
7. Write Recommendation History.
8. Enforce the configured history retention policy.
9. Write the latest JSON state.
10. Append operational logs.
11. Send notifications when applicable.

The console should report successful completion and storage health information.

---

# Immediate Engine Run

Dashboard configuration changes can request an immediate engine execution.

The dashboard creates:

```text
config/run_now.trigger
```

The production launcher checks for this trigger and initiates an engine run.

This allows settings changed through the dashboard to take effect without requiring the operator to manually execute the engine.

The trigger file is removed after it is detected.

---

# Storage Startup Validation

Storage validation is performed before normal engine operation.

The startup validation process ensures that the history database:

- Exists or can be created
- Contains the required schema
- Can be opened successfully
- Passes SQLite integrity validation
- Is suitable for continued engine operation

The validation layer is intended to prevent the engine from silently operating against a damaged history database.

---

# Database Initialization

The history database is self-initializing.

If the configured SQLite database does not exist, the storage layer creates it automatically.

Default database:

```text
state/bch_rental_history.sqlite
```

Manual database creation should not normally be required.

---

# Database Integrity

The storage subsystem performs SQLite integrity validation.

Operators can also manually verify the database.

Open the database:

```bash
sqlite3 state/bch_rental_history.sqlite
```

Run:

```sql
PRAGMA integrity_check;
```

Healthy result:

```text
ok
```

Exit:

```text
.quit
```

If the result is not:

```text
ok
```

do not assume the database is safe.

Preserve a copy before attempting repair or replacement.

---

# Storage Health

Storage health information is exposed by the engine and dashboard.

Current health information includes:

- Database existence
- Database size
- Row count
- Oldest history record
- Newest history record
- SQLite integrity status

The engine also includes storage health information in its latest state output.

Operators should review this information when diagnosing persistence or storage problems.

---

# Storage Dashboard

The dashboard includes a dedicated:

```text
Storage
```

page.

The Storage page provides operator visibility into the Recommendation History database.

It should be used as the primary interface for routine storage monitoring.

Current information includes:

- Database status
- Database size
- Configured retention limit
- Record count
- Oldest record
- Newest record
- Database integrity status
- Storage utilization

The page also provides database maintenance controls where supported.

---

# History Retention

Recommendation History supports configurable size-based retention.

The purpose of retention is to prevent the SQLite database from growing indefinitely on long-running installations.

The effective setting is:

```text
history_max_size_bytes
```

Environment fallback:

```text
BCH_HISTORY_MAX_SIZE_BYTES
```

Default:

```text
1073741824
```

which is:

```text
1 GiB
```

---

# Retention Configuration Precedence

For settings managed through the centralized configuration system, the effective value is resolved using:

```text
Dashboard Override
    ↓
Environment Variable
    ↓
Built-in Default
```

For history retention:

```text
dashboard_config_override.json
    ↓
BCH_HISTORY_MAX_SIZE_BYTES
    ↓
1 GiB
```

This allows production operators to change the retention limit through the dashboard without modifying source code.

---

# Unlimited History

A configured history maximum of:

```text
0
```

means:

```text
Unlimited
```

Example:

```text
BCH_HISTORY_MAX_SIZE_BYTES=0
```

or the equivalent dashboard setting.

When unlimited mode is enabled:

- Automatic size-based pruning is disabled.
- Recommendation History may continue growing indefinitely.
- The operator becomes responsible for monitoring available disk space.

Unlimited retention should only be used when sufficient storage is available.

---

# Automatic History Pruning

When size-based retention is enabled, the engine checks the history database after inserting a new history record.

If the database exceeds the configured maximum:

1. The oldest Recommendation History rows are deleted.
2. Database size is checked again.
3. Additional old rows may be removed if required.
4. Recent history is preserved preferentially.

The goal is to retain the newest and most operationally relevant history while preventing uncontrolled storage growth.

Pruning should not require normal operator intervention.

---

# Important SQLite Retention Behavior

Deleting rows from SQLite does not necessarily reduce the physical database file immediately.

SQLite may retain freed pages internally for reuse.

This means:

```text
row count may decrease
```

without an immediate equivalent decrease in:

```text
database file size
```

This behavior is normal.

Physical file compaction is handled separately.

---

# Database Compaction

Database compaction reclaims unused SQLite pages and reduces the physical database file where possible.

The underlying SQLite operation is:

```sql
VACUUM;
```

Compaction should be treated as a maintenance operation rather than something performed on every engine run.

---

# Manual Database Compaction

The Storage dashboard provides a manual database compaction control.

Use manual compaction when:

- Significant history has been pruned.
- The SQLite file remains larger than expected.
- Disk space should be reclaimed.
- Maintenance is being performed.

Before compacting a production database:

1. Verify the database is healthy.
2. Ensure sufficient temporary disk space exists.
3. Avoid interrupting the operation.
4. Prefer taking a backup when the history is important.

Compaction may temporarily require additional disk space.

---

# Manual SQLite Compaction

If dashboard-based maintenance is unavailable, the database may be compacted manually.

Open SQLite:

```bash
sqlite3 state/bch_rental_history.sqlite
```

Run:

```sql
VACUUM;
```

Exit:

```text
.quit
```

Then verify:

```bash
ls -lh state/bch_rental_history.sqlite
```

Manual SQLite maintenance should be performed carefully in production.

---

# Dashboard Settings

The dashboard includes a:

```text
Settings
```

page.

Current configurable engine controls include:

- Budget minimum
- Budget maximum
- Budget step
- Hashrate minimum
- Hashrate maximum
- Hashrate step
- History retention limit

Settings are persisted to:

```text
config/dashboard_config_override.json
```

After settings are saved, the dashboard requests an immediate engine run.

This allows the engine to regenerate its state using the updated configuration.

---

# Configuration Verification

The effective engine configuration is included in the latest state output.

Inspect:

```bash
python -m json.tool \
state/bch_solo_rental_strike_engine.json
```

The:

```text
config
```

section should reflect the active engine settings.

This includes the effective history retention configuration.

Use the effective state configuration when confirming what the engine actually used during its most recent execution.

---

# Daily Health Check

A normal production health check should take only a few minutes.

Verify:

- Dashboard accessible
- Engine completed successfully
- Latest JSON state updated
- Recommendation generated
- SQLite history updated
- Recommendation History page functioning
- Storage page functioning
- Database integrity healthy
- Storage utilization reasonable
- No unexpected JSONL errors
- Dashboard health check passes
- Telegram alerts functioning if enabled

---

# Dashboard Operations

## Development

Run:

```bash
streamlit run dashboard/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0
```

---

## Production

Verify containers:

```bash
docker ps
```

Dashboard health check:

```bash
./scripts/check_dashboard.sh
```

Restart dashboard:

```bash
./scripts/restart_dashboard.sh
```

Build dashboard:

```bash
./scripts/build_dashboard.sh
```

Deploy dashboard:

```bash
./scripts/deploy_dashboard.sh
```

Update production:

```bash
./scripts/update_dashboard.sh
```

Prefer these helper scripts over manual Docker commands.

---

# Dashboard Verification

After deployment, verify all major pages.

Current pages include:

- Dashboard
- Market
- Market Trends
- Strike Analysis
- Pool Routing
- History
- Storage
- Settings

Verify:

- Navigation works.
- Metrics populate.
- Charts render.
- Recommendation appears.
- History loads.
- Storage information loads.
- Settings display the current configuration.
- No Streamlit exceptions appear.

---

# Recommendation History Verification

Recommendation History powers the historical analytics framework.

Verify:

- SQLite updates after engine execution.
- History page loads.
- Opportunity Score history is visible.
- Historical records are complete.
- Newest record timestamp is current.
- Trend analytics have sufficient history.

---

# Manual History Inspection

Open the database:

```bash
sqlite3 state/bch_rental_history.sqlite
```

List tables:

```sql
.tables
```

Count records:

```sql
SELECT COUNT(*)
FROM run_history;
```

View recent history:

```sql
SELECT *
FROM run_history
ORDER BY id DESC
LIMIT 10;
```

View history range:

```sql
SELECT
    MIN(timestamp) AS oldest_record,
    MAX(timestamp) AS newest_record,
    COUNT(*) AS record_count
FROM run_history;
```

Exit:

```text
.quit
```

---

# Trend Analytics Verification

Current trend analytics include:

- Direction
- Confidence
- Persistence
- Velocity
- Volatility
- Trend Strength

Verify:

- Trends update when sufficient history exists.
- Direction reflects recent observations.
- Confidence appears reasonable.
- Persistence is populated.
- Velocity is populated.
- Volatility classification behaves correctly.
- Trend Strength is consistent with the underlying trend metrics.
- Interpretation text reflects the analytical state.

Insufficient history may legitimately produce limited or unknown trend information.

---

# Viewing Current Recommendation

Pretty-print the latest state:

```bash
python -m json.tool \
state/bch_solo_rental_strike_engine.json
```

Verify:

- Recommendation
- Canonical decision
- Opportunity Score
- Market Regime
- Trend analytics
- Interpretation
- Configuration
- Storage health

---

# Viewing Logs

Engine log:

```bash
tail -50 logs/bch_solo_rental_strike_engine.jsonl
```

Follow engine log:

```bash
tail -f logs/bch_solo_rental_strike_engine.jsonl
```

Alert log:

```bash
tail -50 logs/bch_solo_rental_strike_engine_alerts.jsonl
```

Dashboard container:

```bash
docker logs bch-rental-dashboard
```

Live dashboard logs:

```bash
docker logs -f bch-rental-dashboard
```

---

# JSONL Log Rotation

The engine automatically rotates JSONL logs.

Configuration:

```text
BCH_MAX_JSONL_LOG_BYTES
BCH_MAX_JSONL_LOG_BACKUPS
```

Typical files:

```text
bch_solo_rental_strike_engine.jsonl
bch_solo_rental_strike_engine.jsonl.1
bch_solo_rental_strike_engine.jsonl.2
bch_solo_rental_strike_engine.jsonl.3
```

Older backups are automatically removed according to the configured retention count.

No routine manual JSONL cleanup should be necessary.

---

# Backup Strategy

Back up persistent application data regularly.

Priority directories:

```text
config/
state/
logs/
```

Highest-priority file:

```text
state/bch_rental_history.sqlite
```

Also preserve:

```text
config/dashboard_config_override.json
config/pools.json
```

and any production environment configuration required to recreate the deployment.

---

# SQLite Backup

For a live SQLite database, prefer SQLite's backup mechanism over copying a database during an active write.

Example:

```bash
sqlite3 state/bch_rental_history.sqlite \
  ".backup 'state/bch_rental_history.backup.sqlite'"
```

Verify:

```bash
ls -lh \
  state/bch_rental_history.sqlite \
  state/bch_rental_history.backup.sqlite
```

Check backup integrity:

```bash
sqlite3 state/bch_rental_history.backup.sqlite \
  "PRAGMA integrity_check;"
```

Expected result:

```text
ok
```

---

# Backup Before Maintenance

Create a backup before significant manual database maintenance.

Example:

```bash
sqlite3 state/bch_rental_history.sqlite \
  ".backup 'state/bch_rental_history.pre_maintenance.sqlite'"
```

Then verify:

```bash
sqlite3 state/bch_rental_history.pre_maintenance.sqlite \
  "PRAGMA integrity_check;"
```

Only proceed with invasive maintenance after confirming the backup is healthy.

---

# Restore Procedure

Stop or otherwise prevent concurrent writes before replacing a production database.

Restore the required persistent data:

```text
config/
state/
logs/
```

For a database restore, replace:

```text
state/bch_rental_history.sqlite
```

with the verified backup.

Validate:

```bash
sqlite3 state/bch_rental_history.sqlite \
  "PRAGMA integrity_check;"
```

Expected:

```text
ok
```

Restart application services as required.

For the dashboard:

```bash
./scripts/restart_dashboard.sh
```

Then execute the engine and confirm new history can be written.

A database rebuild should not be required when restoring a valid backup.

---

# Routine Maintenance

## Daily

Verify:

- Dashboard online
- Engine executed
- Latest state current
- SQLite updated
- Recommendation History updated
- Storage health good
- Logs healthy

---

## Weekly

Review:

- Dashboard
- Recommendation History
- Storage page
- Database growth
- Retention utilization
- Backups
- Log growth
- Telegram functionality

Apply production updates when a tested release is available.

---

## Monthly

Perform:

- Database integrity verification
- Backup verification
- Storage utilization review
- Configuration review
- Dependency review
- Docker image rebuild when required
- Disaster-recovery test
- Release documentation review

Database compaction may be performed if significant unused SQLite space has accumulated.

---

# Storage Capacity Planning

The default Recommendation History limit is:

```text
1 GiB
```

This should provide substantial historical capacity for normal engine execution.

Operators who increase the limit should consider:

- Available disk space
- Engine execution frequency
- Expected installation lifetime
- Backup size
- Future historical analytics requirements

Operators using unlimited history should monitor disk usage explicitly.

Example:

```bash
df -h
```

Database size:

```bash
ls -lh state/bch_rental_history.sqlite
```

Directory usage:

```bash
du -sh state
```

---

# Troubleshooting

## Dashboard Unavailable

Check containers:

```bash
docker ps
```

Inspect logs:

```bash
docker logs bch-rental-dashboard
```

Run health check:

```bash
./scripts/check_dashboard.sh
```

Restart if required:

```bash
./scripts/restart_dashboard.sh
```

---

# Engine Failure

Run the engine manually:

```bash
python -m scripts.bch_solo_rental_strike_engine
```

Review:

- Console traceback
- JSONL logs
- Configuration
- Storage health
- API availability
- Network connectivity

---

# Storage Startup Validation Failure

If the engine refuses to continue because storage validation failed:

1. Do not immediately delete the database.
2. Preserve a copy of the current file.
3. Check filesystem permissions.
4. Check available disk space.
5. Run SQLite integrity validation.
6. Restore from a known-good backup if required.

Check integrity:

```bash
sqlite3 state/bch_rental_history.sqlite \
  "PRAGMA integrity_check;"
```

If the result is not:

```text
ok
```

treat the database as potentially damaged.

---

# Recommendation History Not Updating

Verify the database exists:

```bash
ls -lh state/bch_rental_history.sqlite
```

Verify integrity:

```bash
sqlite3 state/bch_rental_history.sqlite \
  "PRAGMA integrity_check;"
```

Verify recent records:

```bash
sqlite3 state/bch_rental_history.sqlite \
  "SELECT id, timestamp FROM run_history ORDER BY id DESC LIMIT 10;"
```

Also verify:

- Engine completed successfully.
- Database directory is writable.
- Database file is writable.
- Startup validation passed.
- No storage exceptions appear in the logs.

---

# History Database Larger Than Configured Limit

First verify the effective retention configuration.

Inspect the latest state:

```bash
python -m json.tool \
state/bch_solo_rental_strike_engine.json
```

Check:

```text
config.history_max_size_bytes
```

If the value is:

```text
0
```

retention is unlimited.

Otherwise remember that deleting SQLite rows does not necessarily immediately shrink the physical file.

If pruning has occurred but the file remains large, use the Storage page's compaction function or perform a controlled:

```sql
VACUUM;
```

after creating a backup.

---

# History Disappearing Faster Than Expected

Check the configured:

```text
history_max_size_bytes
```

and environment fallback:

```text
BCH_HISTORY_MAX_SIZE_BYTES
```

Also inspect:

```text
config/dashboard_config_override.json
```

Remember that the dashboard override takes precedence over the environment fallback.

Increase the configured maximum if more historical depth is required.

---

# Storage Page Shows Unlimited

Unlimited history is expected when the effective history maximum is:

```text
0
```

If this was not intentional, update the History Storage setting through the Settings page or correct the applicable environment configuration.

---

# Database Compaction Fails

Verify:

- Database integrity
- File permissions
- Available disk space
- No conflicting maintenance process
- Database path is correct

Take a backup before retrying.

Do not repeatedly execute destructive maintenance against a database that fails integrity validation.

---

# Settings Changes Not Taking Effect

Verify:

```text
config/dashboard_config_override.json
```

Inspect the current override file from the Settings page.

Then verify the latest engine state:

```bash
python -m json.tool \
state/bch_solo_rental_strike_engine.json
```

Check the:

```text
config
```

section.

Remember that saving dashboard settings requests an immediate engine run, but the latest state must be regenerated before it reflects the new effective configuration.

---

# Immediate Run Not Triggering

Check for:

```text
config/run_now.trigger
```

The production launcher polls for this file.

Verify the launcher is running and that the configuration directory is mounted correctly.

The trigger should be removed after the launcher detects it.

---

# Trend Analytics Missing

Verify:

- Recommendation History exists.
- SQLite contains sufficient observations.
- History retrieval succeeds.
- Engine analytics completed successfully.
- No storage pruning setting is excessively restrictive.

Trend Intelligence requires sufficient historical depth.

A newly installed system may legitimately show limited trend information until additional engine runs accumulate.

---

# Telegram Alerts Missing

Verify:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

For testing only, temporarily enable:

```text
BCH_FORCE_TEST_ALERT=true
```

Run the engine.

Confirm the notification.

Then disable:

```text
BCH_FORCE_TEST_ALERT=false
```

Do not leave forced alerts enabled in normal production operation.

---

# Production Working Tree Is Dirty

Production should remain clean.

Check:

```bash
git status
```

Do not automatically discard unexpected production changes.

Determine why the files changed before proceeding with an update.

Persistent configuration and state should live in their designated directories and mounts rather than as ad hoc modifications to application source.

---

# Operational Recovery Principles

When troubleshooting production:

1. Preserve historical data first.
2. Avoid deleting SQLite databases as a first response.
3. Back up before manual database maintenance.
4. Verify integrity before trusting a recovered database.
5. Prefer application-provided maintenance controls.
6. Prefer production helper scripts over manual container manipulation.
7. Verify effective configuration rather than assuming environment values are active.
8. Run regression-tested releases only.
9. Document unusual recovery actions.

---

# Future Operations Roadmap

Future operational capabilities may include additional system intelligence and automation.

## Monitoring

Planned capabilities include:

- Engine health
- API health
- Pricing source status
- Rental source status
- Background task monitoring
- Resource utilization tracking
- Engine heartbeat
- Automatic diagnostics

---

## Recovery

Planned capabilities include:

- Automatic recovery
- Enhanced startup diagnostics
- Self-test framework
- Backup automation
- Archive management

---

## Alerting

Potential future integrations include:

- Discord
- Email reports
- Webhooks
- Daily market summaries
- Additional operational notifications

---

## Storage

Potential future storage capabilities include:

- Maximum-age retention
- Automatic archival before pruning
- Backup management
- Historical exports
- Archive management
- Historical playback

---

## Deployment

Potential future deployment improvements include:

- Automated releases
- CI/CD integration
- Enhanced container health monitoring
- Additional deployment targets

---

# Operational Checklist

Before considering the system healthy, verify:

```text
[ ] Engine executes successfully
[ ] Storage startup validation passes
[ ] Database integrity is healthy
[ ] Recommendation is generated
[ ] Latest state JSON is written
[ ] Recommendation History receives a row
[ ] Retention policy is correctly configured
[ ] Storage utilization is acceptable
[ ] Dashboard loads
[ ] History page loads
[ ] Storage page loads
[ ] Settings page loads
[ ] Trend analytics are available when sufficient history exists
[ ] JSONL logs are updating
[ ] Telegram works if enabled
[ ] Production working tree is clean
[ ] Backup strategy is functioning
```

---

# Critical Operational Assets

The most important assets to preserve are:

## Recommendation History

```text
state/bch_rental_history.sqlite
```

## Runtime Configuration

```text
config/
```

## Latest Engine State

```text
state/bch_solo_rental_strike_engine.json
```

## Operational Logs

```text
logs/
```

Of these, Recommendation History deserves the highest preservation priority because historical observations cannot be reconstructed after they are lost.

---

# Related Documentation

- [README](../README.md)
- [Architecture Guide](ARCHITECTURE.md)
- [Configuration Reference](CONFIGURATION.md)
- [Recommendation History](RECOMMENDATION_HISTORY.md)
- [Release Checklist](RELEASE_CHECKLIST.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Umbrel Migration](UMBREL_MIGRATION.md)
- [Umbrel Release Process](UMBREL_RELEASE_PROCESS.md)

---

# Operational Principle

The BCH Rental Engine should not require constant operator attention.

The objective of the operational architecture is to allow the engine to run reliably for extended periods while making failures, storage conditions, configuration, and recommendation state visible when an operator needs to investigate them.

The production system should remain:

- Observable
- Recoverable
- Reproducible
- Maintainable
- Storage-aware
- Historically traceable

Protect Recommendation History, verify system health, and prefer controlled operational workflows over manual intervention.