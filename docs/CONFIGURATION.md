# Configuration Reference

This document describes the runtime configuration options available in the BCH Rental Engine.

The engine supports configuration through environment variables and operator-controlled dashboard overrides. Configuration is designed so that the same engine code can run in local development, Docker, and the native Umbrel deployment without hardcoded environment-specific paths or operating parameters.

---

# Configuration Sources

The project currently uses the following configuration files:

```text
config/
├── .env
├── pools.json
└── dashboard_config_override.json
```

| File | Required | Purpose |
|-------|----------|---------|
| `.env` | Environment-dependent | Engine configuration, provider settings, and API credentials |
| `pools.json` | Optional | Pool-specific configuration and metadata |
| `dashboard_config_override.json` | Optional | Operator-controlled engine settings saved through the dashboard |

Environment variables may also be supplied directly by Docker, Umbrel, the shell, or another runtime environment.

---

# Configuration Priority

For settings supported by the dashboard override system, the engine resolves values in the following order:

```text
Dashboard Override
        ↓
Environment Variable
        ↓
Built-in Default
```

For example, the history retention limit is resolved from:

```text
history_max_size_bytes
        ↓
BCH_HISTORY_MAX_SIZE_BYTES
        ↓
1 GiB default
```

This allows an operator to configure defaults through the runtime environment while still making supported operational changes from the dashboard.

Settings that are not currently managed through the dashboard continue to use their environment variable and built-in default behavior.

---

# Environment Variables

Environment variables may be loaded from:

```text
config/.env
```

For a shell-based deployment, they can be loaded using:

```bash
set -a
source config/.env
set +a
```

Docker and Umbrel deployments may provide the same environment variables through their container configuration instead.

API credentials and other secrets should remain outside version control.

---

# Base Directory

## BCH_BASE_DIR

Defines the base runtime directory used by the engine.

Default:

```text
~/bch_rental_engine
```

Example:

```text
BCH_BASE_DIR=/app
```

The base directory is used to derive the default configuration, state, and log directories when those paths are not explicitly overridden.

---

# Configuration Directory

## BCH_CONFIG_DIR

Directory containing runtime configuration files.

Default:

```text
<BCH_BASE_DIR>/config
```

Typical contents:

```text
dashboard_config_override.json
pools.json
mrr_listings.json
```

Docker and Umbrel deployments can mount a persistent configuration directory at this location.

---

# Braiins Configuration

## BRAIINS_BTC_PER_EH_DAY

Rental price override used for Braiins pricing.

Example:

```text
BRAIINS_BTC_PER_EH_DAY=0.50049
```

Units:

```text
BTC / EH / Day
```

---

## BRAIINS_AVAILABLE_PH

Available Braiins hashrate override.

Example:

```text
BRAIINS_AVAILABLE_PH=300
```

Units:

```text
PH/s
```

Example meaning:

```text
300 PH/s available
```

---

# MiningRigRentals Configuration

## MRR_ENABLE_API

Controls whether the MiningRigRentals API integration is enabled.

Example:

```text
MRR_ENABLE_API=true
```

Default:

```text
false
```

---

## MRR_API_KEY

MiningRigRentals API key.

Example:

```text
MRR_API_KEY=xxxxxxxxxxxx
```

Keep this value outside version control.

---

## MRR_API_SECRET

MiningRigRentals API secret.

Example:

```text
MRR_API_SECRET=xxxxxxxxxxxx
```

Keep this value outside version control.

---

## MRR_HASH_MIN_PH

Minimum MiningRigRentals hashrate considered by the marketplace integration.

Example:

```text
MRR_HASH_MIN_PH=50
```

Default:

```text
50
```

---

## MRR_HASH_MAX_PH

Maximum MiningRigRentals hashrate considered by the marketplace integration.

Example:

```text
MRR_HASH_MAX_PH=500
```

Default:

```text
500
```

---

## MRR_COUNT

Maximum listing count requested from the MiningRigRentals integration.

Example:

```text
MRR_COUNT=100
```

Default:

```text
100
```

---

# Budget Optimization

Budget controls determine the range of rental budgets evaluated by the optimization engine.

These settings can be configured through environment variables or the dashboard Settings page.

---

## BCH_STRIKE_BUDGET_MIN_USD

Minimum budget considered by the optimizer.

Example:

```text
BCH_STRIKE_BUDGET_MIN_USD=100
```

Default:

```text
100
```

Dashboard override key:

```text
budget_min_usd
```

---

## BCH_STRIKE_BUDGET_MAX_USD

Maximum budget considered by the optimizer.

Example:

```text
BCH_STRIKE_BUDGET_MAX_USD=1000
```

Default:

```text
1000
```

Dashboard override key:

```text
budget_max_usd
```

---

## BCH_STRIKE_BUDGET_STEP_USD

Budget increment used when evaluating candidate strike plans.

Example:

```text
BCH_STRIKE_BUDGET_STEP_USD=10
```

Default:

```text
10
```

For a range of $100 to $150 with a $10 step, the optimizer evaluates:

```text
100
110
120
130
140
150
```

Dashboard override key:

```text
budget_step_usd
```

---

# Hashrate Optimization

Hashrate controls determine the range of candidate rental hashrates evaluated by the engine.

These settings can be configured through environment variables or the dashboard Settings page.

---

## BCH_HASHRATE_MIN_PH

Minimum hashrate evaluated.

Example:

```text
BCH_HASHRATE_MIN_PH=50
```

Default:

```text
300
```

Dashboard override key:

```text
hashrate_min_ph
```

---

## BCH_HASHRATE_MAX_PH

Maximum hashrate evaluated.

Example:

```text
BCH_HASHRATE_MAX_PH=300
```

Default:

```text
300
```

Dashboard override key:

```text
hashrate_max_ph
```

---

## BCH_HASHRATE_STEP_PH

Hashrate increment used during optimization.

Example:

```text
BCH_HASHRATE_STEP_PH=50
```

Default:

```text
50
```

Dashboard override key:

```text
hashrate_step_ph
```

---

# Rental Duration

## BCH_IDEAL_MIN_HOURS

Preferred minimum rental duration.

Example:

```text
BCH_IDEAL_MIN_HOURS=1.0
```

Default:

```text
1.0
```

---

## BCH_IDEAL_MAX_HOURS

Preferred maximum rental duration.

Example:

```text
BCH_IDEAL_MAX_HOURS=3.0
```

Default:

```text
3.0
```

---

## BCH_ABSOLUTE_MAX_HOURS

Absolute maximum rental duration considered when long rentals are allowed.

Example:

```text
BCH_ABSOLUTE_MAX_HOURS=12.0
```

Default:

```text
12.0
```

---

## BCH_ALLOW_LONG_RENTALS

Controls whether the engine may consider rentals beyond the preferred duration range.

Example:

```text
BCH_ALLOW_LONG_RENTALS=true
```

Default:

```text
true
```

---

# Mining Economics

## BCH_POOL_FEE

Mining pool fee expressed as a decimal.

Example:

```text
BCH_POOL_FEE=0.015
```

Meaning:

```text
1.5%
```

Default:

```text
0.015
```

---

## BCH_ORPHAN_STALE_RISK

Estimated orphan/stale block risk expressed as a decimal.

Example:

```text
BCH_ORPHAN_STALE_RISK=0.005
```

Default:

```text
0.005
```

---

## BCH_RENTAL_EXECUTION_SLIPPAGE_PCT

Execution slippage assumption applied to rental economics.

Example:

```text
BCH_RENTAL_EXECUTION_SLIPPAGE_PCT=0.01
```

Default:

```text
0.01
```

Meaning:

```text
1%
```

---

## BCH_PRICE_MOVE_BUFFER_PCT

Additional safety margin applied to rental pricing.

Example:

```text
BCH_PRICE_MOVE_BUFFER_PCT=0.01
```

Default:

```text
0.01
```

Meaning:

```text
1%
```

This buffer helps account for rental price movement between recommendation generation and execution.

---

## BCH_BLOCK_REWARD

BCH block reward used by the engine.

Example:

```text
BCH_BLOCK_REWARD=3.125
```

Default:

```text
3.125
```

---

# Opportunity Score

The engine combines multiple analytical signals into the Opportunity Score used by the recommendation system.

Current inputs include metrics such as:

- Fair Value Ratio
- Risk-adjusted ROI
- Probability of finding at least one block
- Market regime
- Trend intelligence

Example:

```text
Opportunity Score

54.0 / 100
```

Higher scores indicate stronger rental conditions according to the engine's decision model.

The Opportunity Score is decision support, not a guarantee of mining profitability.

---

# State Directory

## BCH_STATE_DIR

Directory where persistent engine state is stored.

Default:

```text
<BCH_BASE_DIR>/state
```

Example:

```text
BCH_STATE_DIR=~/bch_rental_engine/state
```

Typical contents:

```text
bch_solo_rental_strike_engine.json
bch_rental_history.sqlite
```

The JSON file contains the latest engine state.

The SQLite database contains Recommendation History and supports historical analytics and Trend Intelligence.

---

# History Storage Retention

Recommendation History is stored in:

```text
state/bch_rental_history.sqlite
```

The storage subsystem is self-initializing and supports:

- Automatic database creation
- Schema versioning
- Sequential schema migrations
- Database integrity checks
- Startup validation
- Storage statistics
- Automatic size-based retention
- SQLite compaction
- Unlimited-history mode

---

## BCH_HISTORY_MAX_SIZE_BYTES

Controls the maximum size of the SQLite Recommendation History database.

Default:

```text
1073741824
```

This is:

```text
1 GiB
```

Example — 2 GiB:

```text
BCH_HISTORY_MAX_SIZE_BYTES=2147483648
```

Dashboard override key:

```text
history_max_size_bytes
```

When the configured limit is exceeded, the storage subsystem removes the oldest Recommendation History records and compacts the SQLite database.

The retention process preserves the newest historical observations while preventing uncontrolled long-term database growth.

---

## Unlimited History

Set the maximum size to `0` to disable size-based history pruning.

Environment variable:

```text
BCH_HISTORY_MAX_SIZE_BYTES=0
```

Dashboard equivalent:

```text
history_max_size_bytes = 0
```

A value of `0` means:

```text
Unlimited
```

Unlimited mode should only be used when available disk space is monitored independently.

---

# Storage Startup Validation

The engine validates its SQLite storage subsystem during startup before beginning the normal decision workflow.

Startup validation:

1. Ensures the database exists.
2. Initializes the required schema when necessary.
3. Applies supported schema migrations.
4. Performs an integrity check.
5. Stops startup if database integrity validation fails.

This protects the engine from continuing normal operation against a database that fails its integrity check.

---

# Storage Dashboard

The dashboard includes a dedicated Storage page for inspecting Recommendation History storage.

The page displays:

- Current database size
- Configured maximum database size
- Record count
- Oldest record timestamp
- Newest record timestamp
- Database health
- Integrity status

The Storage page also provides a manual:

```text
Compact Database
```

control.

Manual compaction uses SQLite `VACUUM` to reclaim unused database space.

---

# Log Directory

## BCH_LOG_DIR

Location of JSONL logs.

Default:

```text
<BCH_BASE_DIR>/logs
```

Example:

```text
BCH_LOG_DIR=~/bch_rental_engine/logs
```

Typical contents:

```text
bch_solo_rental_strike_engine.jsonl
bch_solo_rental_strike_engine_alerts.jsonl
```

---

# JSON Log Rotation

## BCH_MAX_JSONL_LOG_BYTES

Maximum size of a JSONL log before rotation.

Example:

```text
BCH_MAX_JSONL_LOG_BYTES=10485760
```

Typical default:

```text
10 MB
```

---

## BCH_MAX_JSONL_LOG_BACKUPS

Number of archived JSONL logs retained.

Example:

```text
BCH_MAX_JSONL_LOG_BACKUPS=5
```

Typical result:

```text
engine.jsonl
engine.jsonl.1
engine.jsonl.2
engine.jsonl.3
engine.jsonl.4
engine.jsonl.5
```

Older rotated logs are automatically removed according to the configured backup count.

---

# Runtime and Network Options

## BCH_REQUEST_TIMEOUT

Network request timeout used by the engine.

Example:

```text
BCH_REQUEST_TIMEOUT=20
```

Default:

```text
20
```

---

## BCH_MAX_RETRIES

Maximum retry count used for supported network operations.

Example:

```text
BCH_MAX_RETRIES=3
```

Default:

```text
3
```

---

# Telegram Configuration

Telegram alerts are optional.

## TELEGRAM_BOT_TOKEN

Telegram bot token.

Example:

```text
TELEGRAM_BOT_TOKEN=
```

Keep this value outside version control.

---

## TELEGRAM_CHAT_ID

Telegram destination chat ID.

Example:

```text
TELEGRAM_CHAT_ID=
```

The engine also supports `TELEGRAM_HOME_CHANNEL` as a fallback when `TELEGRAM_CHAT_ID` is not defined.

When Telegram is configured, the engine can send recommendation alerts according to its alert logic.

---

# Testing Options

## BCH_FORCE_TEST_ALERT

Forces Telegram alert behavior for testing.

Example:

```text
BCH_FORCE_TEST_ALERT=true
```

Recommended production value:

```text
false
```

Use this only during controlled testing.

---

# Dashboard Configuration

The Streamlit dashboard reads and writes:

```text
config/dashboard_config_override.json
```

This file stores operator-controlled engine settings without requiring Python code changes.

Current dashboard-configurable settings include:

- Budget minimum
- Budget maximum
- Budget step
- Hashrate minimum
- Hashrate maximum
- Hashrate step
- History maximum database size

Example:

```json
{
  "budget_max_usd": 1000,
  "budget_min_usd": 100,
  "budget_step_usd": 10,
  "hashrate_max_ph": 300,
  "hashrate_min_ph": 300,
  "hashrate_step_ph": 50,
  "history_max_size_bytes": 1073741824
}
```

For supported settings, dashboard overrides take precedence over corresponding environment variables.

The dashboard Settings page writes changes to this file and can request an immediate engine run so that the new configuration is applied.

---

# Effective Runtime Configuration

The engine publishes its effective operational configuration in the latest state JSON.

File:

```text
state/bch_solo_rental_strike_engine.json
```

The state includes a:

```text
config
```

object containing resolved runtime values such as:

- Budget range
- Hashrate range
- Duration limits
- Mining economics
- History maximum database size

This allows the dashboard to report the configuration actually being used by the engine rather than relying only on static defaults.

---

# Default Configuration Example

The following is a representative environment configuration:

```text
# Paths
BCH_BASE_DIR=~/bch_rental_engine
BCH_STATE_DIR=~/bch_rental_engine/state
BCH_LOG_DIR=~/bch_rental_engine/logs
BCH_CONFIG_DIR=~/bch_rental_engine/config

# Braiins
BRAIINS_BTC_PER_EH_DAY=0.50049
BRAIINS_AVAILABLE_PH=300

# MiningRigRentals
MRR_ENABLE_API=false
MRR_API_KEY=
MRR_API_SECRET=
MRR_HASH_MIN_PH=50
MRR_HASH_MAX_PH=500
MRR_COUNT=100

# Budget optimization
BCH_STRIKE_BUDGET_MIN_USD=100
BCH_STRIKE_BUDGET_MAX_USD=1000
BCH_STRIKE_BUDGET_STEP_USD=10

# Hashrate optimization
BCH_HASHRATE_MIN_PH=300
BCH_HASHRATE_MAX_PH=300
BCH_HASHRATE_STEP_PH=50

# Rental duration
BCH_IDEAL_MIN_HOURS=1.0
BCH_IDEAL_MAX_HOURS=3.0
BCH_ABSOLUTE_MAX_HOURS=12.0
BCH_ALLOW_LONG_RENTALS=true

# Mining economics
BCH_POOL_FEE=0.015
BCH_ORPHAN_STALE_RISK=0.005
BCH_RENTAL_EXECUTION_SLIPPAGE_PCT=0.01
BCH_PRICE_MOVE_BUFFER_PCT=0.01
BCH_BLOCK_REWARD=3.125

# Recommendation History retention
BCH_HISTORY_MAX_SIZE_BYTES=1073741824

# Runtime
BCH_REQUEST_TIMEOUT=20
BCH_MAX_RETRIES=3

# JSONL log rotation
BCH_MAX_JSONL_LOG_BYTES=10485760
BCH_MAX_JSONL_LOG_BACKUPS=5

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# Testing
BCH_FORCE_TEST_ALERT=false
```

---

# Recommended History Retention

For normal operation, the recommended configuration is:

```text
BCH_HISTORY_MAX_SIZE_BYTES=1073741824
```

This provides a 1 GiB maximum for Recommendation History.

Increase the value when:

- Longer historical retention is required.
- Historical analytics need a deeper observation window.
- Sufficient persistent disk capacity is available.

Decrease the value when:

- The application is running on constrained storage.
- Only recent Recommendation History is required.

Use:

```text
BCH_HISTORY_MAX_SIZE_BYTES=0
```

only when unlimited history is intentional and disk growth is monitored independently.

---

# Best Practices

- Keep API credentials and secrets out of version control.
- Never commit production `.env` files containing credentials.
- Use persistent volumes for `config/`, `state/`, and other operational data in production.
- Back up the `state/` directory regularly.
- Treat `bch_rental_history.sqlite` as an important operational asset.
- Keep the default 1 GiB Recommendation History limit unless longer retention is operationally required.
- Use unlimited Recommendation History only when disk growth is monitored independently.
- Review the Storage dashboard periodically.
- Investigate failed SQLite integrity checks before restarting normal engine operation.
- Use the dashboard Settings page for supported operator-controlled settings.
- Use environment variables for deployment-specific defaults and secrets.
- Keep budget and hashrate ranges realistic to reduce optimization time.
- Review JSONL log growth periodically.
- Test configuration changes before production use.
- Back up persistent data before major upgrades or migrations.

---

# Configuration Verification

After changing configuration, verify the effective values through the dashboard or the latest state file.

For example:

```bash
python -m json.tool \
  state/bch_solo_rental_strike_engine.json
```

Review the:

```text
config
```

object and confirm that the expected values are active.

For storage configuration, also verify the dashboard Storage page shows the expected retention limit and healthy database status.

---

# Next Steps

After configuring the engine, continue with:

- [Architecture Guide](ARCHITECTURE.md)
- [Operations Runbook](OPERATIONS.md)
- [Recommendation History](RECOMMENDATION_HISTORY.md)
- [Installation Guide](INSTALL.md)
- [Umbrel Release Process](UMBREL_RELEASE_PROCESS.md)