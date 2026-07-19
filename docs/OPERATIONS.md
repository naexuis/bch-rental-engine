# Operations Runbook

The Operations Runbook describes the day-to-day administration of the BCH Rental Engine.

This document is intended for anyone responsible for operating, monitoring, maintaining, or updating the system.

---

# Daily Health Check

A normal daily health check should take less than two minutes.

Verify:

- Dashboard is accessible
- Engine completed its most recent execution
- SQLite database is updating
- JSON state file has a recent timestamp
- No abnormal errors in JSONL logs
- Telegram alerts are functioning (optional)

---

# Directory Layout

```
~/bch_rental_engine/

config/
logs/
state/
```

Important files:

```
config/.env

state/bch_solo_rental_strike_engine.json

state/bch_rental_history.sqlite

logs/bch_solo_rental_strike_engine.jsonl

logs/bch_solo_rental_strike_engine_alerts.jsonl
```

---

# Starting the Engine

Load the environment:

```bash
set -a
source config/.env
set +a
```

Run:

```bash
python scripts/bch_solo_rental_strike_engine.py
```

Expected output:

```
Recommendation: WATCH

Market Regime: FAIR

Opportunity Score: 54.0
```

---

# Starting the Dashboard

Development:

```bash
streamlit run dashboard/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0
```

Production (Docker)

```
docker ps
```

Expected

```
bch-rental-dashboard

STATUS

Up
```

---

# Updating the Repository

Navigate to the repository:

```bash
cd ~/projects/bch-rental-engine
```

Switch to the main branch:

```bash
git checkout main
```

Pull updates:

```bash
git pull origin main
```

---

# Updating Umbrel Dashboard

Pull the latest code:

```bash
git checkout main

git pull origin main
```

Stop the existing container:

```bash
sudo docker stop bch-rental-dashboard

sudo docker rm bch-rental-dashboard
```

Build:

```bash
sudo docker build \
    -f Dockerfile.dashboard \
    -t bch-rental-dashboard .
```

Run:

```bash
sudo docker run -d \
    --name bch-rental-dashboard \
    --restart unless-stopped \
    -p 8501:8501 \
    -v ~/bch_rental_engine/state:/root/bch_rental_engine/state \
    -v ~/bch_rental_engine/config:/root/bch_rental_engine/config \
    bch-rental-dashboard
```

Verify:

```bash
docker ps
```

---

# Viewing Logs

Engine log

```bash
tail -50 \
~/bch_rental_engine/logs/bch_solo_rental_strike_engine.jsonl
```

Alert log

```bash
tail -50 \
~/bch_rental_engine/logs/bch_solo_rental_strike_engine_alerts.jsonl
```

Docker logs

```bash
docker logs bch-rental-dashboard
```

Follow live logs

```bash
docker logs -f bch-rental-dashboard
```

---

# Viewing Current Recommendation

Inspect the JSON state:

```bash
cat \
~/bch_rental_engine/state/bch_solo_rental_strike_engine.json
```

Pretty-print:

```bash
python -m json.tool \
~/bch_rental_engine/state/bch_solo_rental_strike_engine.json
```

---

# Checking Database Health

Open SQLite

```bash
sqlite3 \
~/bch_rental_engine/state/bch_rental_history.sqlite
```

List tables

```sql
.tables
```

Recent runs

```sql
SELECT *
FROM run_history
ORDER BY id DESC
LIMIT 10;
```

Exit

```
.quit
```

---

# Checking Disk Usage

Logs

```bash
du -sh \
~/bch_rental_engine/logs
```

State

```bash
du -sh \
~/bch_rental_engine/state
```

Entire project

```bash
du -sh \
~/projects/bch-rental-engine
```

---

# Backups

The following should be backed up regularly.

```
config/

state/

logs/
```

The SQLite database is the most valuable file.

```
state/bch_rental_history.sqlite
```

---

# Restoring From Backup

Restore

```
config/

state/

logs/
```

Restart the dashboard.

No database rebuild is required.

---

# Log Rotation

Operational logs rotate automatically.

Configuration

```
BCH_MAX_JSONL_LOG_BYTES

BCH_MAX_JSONL_LOG_BACKUPS
```

Example

```
engine.jsonl

engine.jsonl.1

engine.jsonl.2

engine.jsonl.3
```

No manual cleanup should normally be required.

---

# Updating Python Packages

Activate the virtual environment

```bash
source venv/bin/activate
```

Upgrade

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

---

# Updating Docker Image

Rebuild

```bash
docker build \
-f Dockerfile.dashboard \
-t bch-rental-dashboard .
```

Restart

```bash
docker restart bch-rental-dashboard
```

---

# Common Maintenance Tasks

## Verify dashboard

```
http://SERVER_IP:8501
```

Check

- Decision Center
- Market Overview
- Strike Analysis
- Historical charts
- Candlestick charts

---

## Verify engine

Run

```bash
python scripts/bch_solo_rental_strike_engine.py
```

Ensure

- Recommendation generated
- SQLite updated
- JSON updated

---

## Verify Telegram

Temporarily enable

```
BCH_FORCE_TEST_ALERT=true
```

Run engine.

Confirm message received.

Return

```
BCH_FORCE_TEST_ALERT=false
```

---

# Troubleshooting

## Dashboard won't load

Check

```bash
docker ps
```

Then

```bash
docker logs bch-rental-dashboard
```

---

## Engine fails

Run

```bash
python scripts/bch_solo_rental_strike_engine.py
```

Inspect

```
logs/

JSONL
```

---

## SQLite not updating

Verify

```
state/
```

permissions.

Confirm engine completed successfully.

---

## Recommendation missing

Inspect

```
bch_solo_rental_strike_engine.json
```

Verify

```
winners

best_strike
```

exists.

---

## No market data

Check internet connectivity.

Verify CoinGecko is reachable.

Verify Braiins configuration.

---

## No Telegram alerts

Verify

```
TELEGRAM_BOT_TOKEN

TELEGRAM_CHAT_ID
```

Run with

```
BCH_FORCE_TEST_ALERT=true
```

---

# Weekly Maintenance

Recommended once per week.

- Review dashboard
- Check database growth
- Review log sizes
- Update repository
- Verify backups
- Test Telegram
- Review Opportunity Score history
- Review recommendation history

---

# Monthly Maintenance

Recommended once per month.

- Upgrade Python packages
- Update Docker image
- Pull latest Git changes
- Verify backups
- Archive historical database
- Review disk usage
- Review configuration values
- Test complete engine restart

---

# Disaster Recovery Checklist

If moving to a new server:

Restore

- Repository
- config/
- state/
- logs/

Install dependencies.

Load environment variables.

Start engine.

Start dashboard.

Verify dashboard.

Verify SQLite history.

Verify Telegram.

System should resume without data loss.

---

# Operational Checklist

Daily

- ✅ Dashboard online
- ✅ Engine completed successfully
- ✅ JSON updated
- ✅ SQLite updated
- ✅ Logs healthy

Weekly

- ✅ Pull latest Git updates
- ✅ Review log growth
- ✅ Verify backups

Monthly

- ✅ Upgrade dependencies
- ✅ Test restore procedure
- ✅ Review configuration
- ✅ Verify Docker deployment

---

# Next Steps

Continue with:

- [Deploy to EC2](DEPLOY_EC2.md)
- [Decision Log](DECISION_LOG.md)
- [Developer Journal](DEVELOPER_JOURNAL.md)