# Operations Runbook

The Operations Runbook describes the day-to-day administration of the BCH Rental Engine.

It is intended for operators responsible for deploying, monitoring, maintaining, and troubleshooting the production environment while keeping development isolated.

---

# Operational Philosophy

The BCH Rental Engine uses two completely separate environments.

## Development

Purpose

- Feature development
- Test-Driven Development (TDD)
- Unit testing
- Documentation updates
- Experimental work

Location

```text
~/projects/bch-rental-engine
```

Characteristics

- Frequent commits
- May contain unfinished work
- Safe to modify
- Never serves production traffic

---

## Production

Purpose

- Stable engine execution
- Dashboard hosting
- Historical data collection
- Operator access

Location

```text
~/bch_rental_engine
```

Characteristics

- Dockerized dashboard
- Stable releases only
- Working tree always clean
- Updated only through the deployment workflow

Development should never be performed directly in the production repository.

---

# Standard Release Workflow

Every production release follows the same sequence.

```
Development

↓

TDD Complete

↓

Regression Tests

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

Health Check

↓

Production Verification
```

Only tagged, tested releases should be deployed to production.

---

# Standard Umbrel Update Workflow

The preferred deployment method is:

```bash
cd ~/bch_rental_engine

./scripts/update_dashboard.sh
```

The update script automatically:

1. Verifies the working tree is clean.
2. Fetches the latest Git commits and tags.
3. Performs a fast-forward pull.
4. Builds the Docker dashboard image.
5. Replaces the running container.
6. Waits for the dashboard to become available.
7. Executes the dashboard health check.

Manual Docker commands should rarely be necessary.

---

# Repository Layout

## Development

```text
~/projects/bch-rental-engine
```

---

## Production

```text
~/bch_rental_engine
```

Important directories

```text
config/
dashboard/
docs/
logs/
scripts/
state/
tests/
```

Critical files

```text
config/.env

state/bch_solo_rental_strike_engine.json

state/bch_rental_history.sqlite

logs/bch_solo_rental_strike_engine.jsonl

config/pools.json
```

---

# Daily Health Check

A normal health check should take less than two minutes.

Verify

- Dashboard accessible
- Engine completed successfully
- Latest JSON state updated
- SQLite history growing
- Recommendation History updating
- No JSONL errors
- Dashboard health check passes
- Telegram alerts functioning (optional)

---

# Engine Execution

Load environment variables

```bash
set -a
source config/.env
set +a
```

Run the engine

```bash
python scripts/bch_solo_rental_strike_engine.py
```

Verify

- Recommendation generated
- SQLite updated
- JSON state written
- JSONL log appended

---

# Dashboard Operations

## Development

```bash
streamlit run dashboard/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0
```

---

## Production

Verify container

```bash
docker ps
```

Health check

```bash
./scripts/check_dashboard.sh
```

Restart

```bash
./scripts/restart_dashboard.sh
```

Build

```bash
./scripts/build_dashboard.sh
```

Deploy

```bash
./scripts/deploy_dashboard.sh
```

Update

```bash
./scripts/update_dashboard.sh
```

---

# Recommendation History Verification

Recommendation History powers the analytics framework.

Verify

- SQLite updates every engine execution
- Recommendation History page loads
- Opportunity Score history visible
- Historical records complete

Trend analytics should be generated from Recommendation History.

---

# Trend Analytics Verification

Current analytics include

- Direction
- Confidence
- Persistence
- Velocity
- Volatility
- Trend Strength

Verify

- Trends update correctly
- Confidence appears reasonable
- Velocity values are populated
- Volatility classification behaves correctly
- Trend strength matches expectations

---

# Viewing Logs

Engine

```bash
tail -50 logs/bch_solo_rental_strike_engine.jsonl
```

Follow

```bash
tail -f logs/bch_solo_rental_strike_engine.jsonl
```

Docker

```bash
docker logs bch-rental-dashboard
```

Live Docker logs

```bash
docker logs -f bch-rental-dashboard
```

---

# Viewing Current Recommendation

Pretty-print

```bash
python -m json.tool \
state/bch_solo_rental_strike_engine.json
```

Verify

- Recommendation
- Opportunity Score
- Market Regime
- Trend analytics
- Interpretation

---

# SQLite Verification

Open database

```bash
sqlite3 state/bch_rental_history.sqlite
```

List tables

```sql
.tables
```

Recent history

```sql
SELECT *
FROM run_history
ORDER BY id DESC
LIMIT 10;
```

Exit

```text
.quit
```

---

# Log Rotation

The engine automatically rotates JSONL logs.

Configuration

```text
BCH_MAX_JSONL_LOG_BYTES

BCH_MAX_JSONL_LOG_BACKUPS
```

Typical files

```text
engine.jsonl

engine.jsonl.1

engine.jsonl.2

engine.jsonl.3
```

No manual cleanup is normally required.

---

# Backup Strategy

Back up regularly

```text
config/

state/

logs/
```

Highest priority

```text
state/bch_rental_history.sqlite
```

Recommendation History is the engine's most valuable operational asset.

---

# Restore Procedure

Restore

```text
config/

state/

logs/
```

Restart

```bash
./scripts/restart_dashboard.sh
```

No database rebuild is required.

---

# Routine Maintenance

## Daily

- Dashboard online
- Engine executed
- SQLite updated
- Recommendation History updated
- Logs healthy

---

## Weekly

- Review dashboard
- Review Recommendation History
- Verify backups
- Review log growth
- Pull Git updates
- Test Telegram

---

## Monthly

- Upgrade dependencies
- Rebuild Docker image
- Archive SQLite database
- Review configuration
- Test disaster recovery
- Verify release documentation

---

# Troubleshooting

## Dashboard unavailable

```bash
docker ps

docker logs bch-rental-dashboard
```

---

## Engine failure

```bash
python scripts/bch_solo_rental_strike_engine.py
```

Review

- JSONL logs
- Stack trace
- Configuration

---

## Recommendation History not updating

Verify

- SQLite permissions
- Engine completed
- Database writable

---

## Trend analytics missing

Verify

- Recommendation History exists
- Sufficient historical observations
- Analytics layer completed successfully

---

## Telegram alerts missing

Temporarily enable

```text
BCH_FORCE_TEST_ALERT=true
```

Run engine.

Confirm notification.

Disable afterward.

---

# Future Operations Roadmap

Operational capabilities planned for future releases include:

## Monitoring

- Automated health monitoring
- Docker health metrics
- Engine heartbeat
- Resource utilization tracking

---

## Alerting

- Slack notifications
- Discord notifications
- Email reports
- SMS alerts

---

## Forecast Operations

- Forecast dashboard
- Trend reversal alerts
- Strike countdowns
- Opportunity forecasting

---

## Deployment

- EC2 deployment
- Blue/Green deployment
- Automated releases
- CI/CD integration

---

# Related Documentation

- CHANGELOG.md
- ROADMAP.md
- RECOMMENDATION_HISTORY.md
- RELEASE_CHECKLIST.md
- DEPLOYMENT_V2.md
- ARCHITECTURE.md