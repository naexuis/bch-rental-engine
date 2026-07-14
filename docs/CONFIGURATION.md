# Configuration Reference

This document describes every configuration option available in the BCH Solo Rental Strike Engine.

The engine is configured primarily through environment variables loaded from the `config/.env` file. Optional JSON configuration files may also be used for dashboard customization and future engine extensions.

---

# Configuration Files

The project currently uses the following configuration files:

```
config/
├── .env
├── pools.json
└── dashboard_config_override.json
```

| File | Required | Purpose |
|-------|----------|---------|
| `.env` | Yes | Engine configuration and API credentials |
| `pools.json` | Optional | Pool-specific overrides and metadata |
| `dashboard_config_override.json` | Optional | Dashboard appearance and behavior |

---

# Environment Variables

The engine loads variables from:

```
config/.env
```

using

```bash
set -a
source config/.env
set +a
```

---

# Braiins Configuration

## BRAIINS_BTC_PER_EH_DAY

Current rental price used when the Braiins API is unavailable.

Example

```text
BRAIINS_BTC_PER_EH_DAY=0.50049
```

Units

```
BTC / EH / Day
```

Required

✅ Yes (unless live Braiins pricing is enabled)

---

## BRAIINS_AVAILABLE_PH

Maximum rentable hashrate available from Braiins.

Example

```text
BRAIINS_AVAILABLE_PH=300
```

Units

```
PH/s
```

Example meaning

```
300 PH/s available
```

---

# MiningRigRentals Configuration

If MiningRigRentals support is enabled, configure the required API credentials.

Example

```text
MRR_API_KEY=xxxxxxxxxxxx

MRR_API_SECRET=xxxxxxxxxxxx
```

These credentials allow the engine to retrieve current marketplace pricing.

---

# Budget Optimization

## BUDGET_MIN_USD

Minimum budget considered by the optimizer.

Example

```text
BUDGET_MIN_USD=100
```

---

## BUDGET_MAX_USD

Maximum budget evaluated.

Example

```text
BUDGET_MAX_USD=750
```

---

## BUDGET_STEP_USD

Optimizer increment.

Example

```text
BUDGET_STEP_USD=10
```

The optimizer will evaluate

```
100
110
120
130
...
750
```

---

# Hashrate Optimization

## HASHRATE_MIN_PH

Minimum hashrate evaluated.

Example

```text
HASHRATE_MIN_PH=50
```

---

## HASHRATE_MAX_PH

Maximum hashrate evaluated.

Example

```text
HASHRATE_MAX_PH=300
```

---

## HASHRATE_STEP_PH

Hashrate increment.

Example

```text
HASHRATE_STEP_PH=10
```

The optimizer evaluates

```
50
60
70
...
300
```

---

# Mining Economics

## POOL_FEE

Mining pool fee expressed as a decimal.

Example

```text
POOL_FEE=0.015
```

Meaning

```
1.5%
```

---

## PRICE_MOVE_BUFFER_PCT

Additional safety margin applied to rental pricing.

Example

```text
PRICE_MOVE_BUFFER_PCT=0.05
```

Meaning

```
5%
```

This buffer protects against sudden increases in rental pricing between recommendation and execution.

---

# Opportunity Score

The engine combines several metrics into a single Opportunity Score.

Current components include

- Fair Value Ratio
- Risk-adjusted ROI
- Probability of finding at least one block
- Market Regime

Example

```
Opportunity Score

54.0 / 100
```

Higher scores indicate more attractive rental opportunities.

---

# Telegram Configuration

Telegram alerts are optional.

Required variables

```text
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

When configured, the engine automatically sends notifications whenever a recommendation changes significantly.

---

# State Directory

## BCH_STATE_DIR

Directory where engine output is stored.

Example

```text
BCH_STATE_DIR=~/bch_rental_engine/state
```

Contains

```
bch_solo_rental_strike_engine.json

bch_rental_history.sqlite
```

---

# Log Directory

## BCH_LOG_DIR

Location of JSONL logs.

Example

```text
BCH_LOG_DIR=~/bch_rental_engine/logs
```

Contains

```
bch_solo_rental_strike_engine.jsonl

bch_solo_rental_strike_engine_alerts.jsonl
```

---

# JSON Log Rotation

## BCH_MAX_JSONL_LOG_BYTES

Maximum size of a JSONL log before rotation.

Example

```text
BCH_MAX_JSONL_LOG_BYTES=10485760
```

Default

```
10 MB
```

---

## BCH_MAX_JSONL_LOG_BACKUPS

Number of archived logs retained.

Example

```text
BCH_MAX_JSONL_LOG_BACKUPS=5
```

Result

```
engine.jsonl

engine.jsonl.1

engine.jsonl.2

engine.jsonl.3

engine.jsonl.4

engine.jsonl.5
```

Older logs are automatically deleted.

---

# Testing Options

## BCH_FORCE_TEST_ALERT

Forces Telegram alerts regardless of recommendation.

Example

```text
BCH_FORCE_TEST_ALERT=true
```

Recommended

```
false
```

Useful during development.

---

# Dashboard Configuration

The Streamlit dashboard reads

```
dashboard_config_override.json
```

This file can override dashboard defaults without modifying Python code.

Future versions will expose these settings directly through the dashboard.

---

# Default Configuration Example

```text
BRAIINS_BTC_PER_EH_DAY=0.50049
BRAIINS_AVAILABLE_PH=300

BUDGET_MIN_USD=100
BUDGET_MAX_USD=750
BUDGET_STEP_USD=10

HASHRATE_MIN_PH=50
HASHRATE_MAX_PH=300
HASHRATE_STEP_PH=10

POOL_FEE=0.015

PRICE_MOVE_BUFFER_PCT=0.05

BCH_STATE_DIR=~/bch_rental_engine/state
BCH_LOG_DIR=~/bch_rental_engine/logs

BCH_MAX_JSONL_LOG_BYTES=10485760
BCH_MAX_JSONL_LOG_BACKUPS=5

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

---

# Best Practices

- Keep API credentials out of version control.
- Never commit your `.env` file.
- Back up the `state/` directory regularly.
- Back up the SQLite history database.
- Review log file sizes periodically.
- Keep budget and hashrate ranges realistic to reduce optimization time.
- Use environment variables instead of hardcoding values.
- Test configuration changes before running production optimizations.

---

# Next Steps

After configuring the engine, continue with:

- [Architecture Guide](ARCHITECTURE.md)
- [Operations Runbook](OPERATIONS.md)
- [Deploy to EC2](DEPLOY_EC2.md)