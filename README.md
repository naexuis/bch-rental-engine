# BCH Rental Engine

A self-hosted, explainable decision-support platform for evaluating Bitcoin Cash (BCH) solo-mining hashpower rental opportunities.

The BCH Rental Engine combines live market data, network conditions, hashpower rental pricing, statistical block-probability modeling, risk-adjusted economics, historical intelligence, trend analysis, pool routing, explainable decision logic, operational monitoring, and an operator-focused dashboard.

The system is designed to answer one primary question:

> **Should I rent hashpower right now?**

More importantly, it explains:

- Why the recommendation was made
- What changed since previous evaluations
- What is preventing a stronger recommendation
- Which direction market conditions are moving
- How attractive the current opportunity is
- What conditions would need to improve before renting

The objective is not to automate mining decisions.

The objective is to make those decisions transparent, measurable, reproducible, and explainable.

---

# Contents

- [Project Status](#project-status)
- [Core Capabilities](#core-capabilities)
- [Decision Architecture](#decision-architecture)
- [System Architecture](#system-architecture)
- [Storage and Reliability](#storage-and-reliability)
- [Dashboard](#dashboard)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Docker](#docker)
- [Umbrel](#umbrel)
- [Configuration](#configuration)
- [Main Outputs](#main-outputs)
- [Testing](#testing)
- [Development Workflow](#development-workflow)
- [Safety](#safety)
- [Documentation](#documentation)
- [Roadmap](#roadmap)

---

# Project Status

**Current Release Line:** `v0.2.x`

**Current Milestone:** Storage & Reliability

**Status:** Release Hardening

**Platform:** Native Umbrel Application

The current release line is:

```text
v0.1 — Foundation
v0.2 — Storage & Reliability
v0.3 — System Intelligence
v0.4 — Forecast Intelligence
v0.5 — Historical Intelligence
v0.6 — Operator Experience
v0.7 — Automation
v0.8 — Strategy Lab
v0.9 — Multi-Coin Platform
v1.0 — BCH Rental Intelligence Platform
```

Version 0.1 established the application foundation.

Version 0.2 expands that foundation with production-oriented storage management, schema migration, history retention, database health monitoring, startup validation, configuration management, and operator-facing storage controls.

The Version 0.2 feature implementation is substantially complete.

Current work is focused on:

- Release hardening
- Runtime validation
- Docker validation
- Umbrel production validation
- Documentation consistency
- Final release tagging

---

# Core Capabilities

## Market Intelligence

The engine collects and evaluates:

- BCH market price
- BTC market price
- BCH network difficulty
- Estimated network hashrate
- Rental marketplace pricing
- Available rental hashrate

Current rental integrations include:

- Braiins
- MiningRigRentals

---

## Rental Optimization

The engine evaluates executable combinations of:

- Budget
- Hashrate
- Rental duration
- Rental source
- Rental price

Current optimization capabilities include:

- Budget range optimization
- Hashrate range optimization
- Rental-duration evaluation
- Budget frontier analysis
- Optimization-surface analysis
- Alternative strike-plan generation

---

## Mining Economics

Each executable scenario can evaluate:

- Expected blocks
- Probability of finding at least one block
- Expected revenue
- Expected profit
- ROI
- Risk-adjusted ROI
- Fair Value Ratio
- Rental premium or discount
- Pool fees
- Orphan/stale risk
- Execution slippage
- Price-movement buffers

Solo-mining probability is modeled statistically rather than treated as a deterministic outcome.

---

## Decision Intelligence

The engine provides:

- Canonical operator decision
- Recommendation
- Opportunity Action
- Alert Tier
- Opportunity Score
- Market Regime
- Recommendation reasoning
- Current blockers
- Conditions required for stronger recommendations

---

## Historical Intelligence

Recommendation History provides the evidence base for longitudinal analysis.

Current capabilities include:

- SQLite historical persistence
- Historical metric retrieval
- Latest-value retrieval
- Historical trend windows
- Recommendation changes
- Opportunity Score changes
- Historical comparisons
- Storage statistics

---

## Trend Intelligence

Current Trend Intelligence includes:

- Direction
- Confidence
- Persistence
- Velocity
- Volatility
- Trend Strength
- High-velocity trend promotion
- Interpretation integration

Trend Intelligence helps the operator understand not only current conditions, but how those conditions are evolving.

---

## Pool Routing

The engine evaluates mining-pool options and provides:

- Pool rankings
- Recommended pool
- Pool-specific information
- Operator-facing routing guidance

---

## Notifications

Current notification capabilities include:

- Telegram alerts
- Recommendation summaries
- Recommendation-change alerts

---

# Decision Architecture

The BCH Rental Engine uses a **Canonical Decision Architecture**.

Business decisions should be made once and then consumed by downstream systems.

The primary decision function is:

```text
determine_canonical_decision()
```

Current canonical decisions are:

```text
RENT_NOW
READY
WATCH_CLOSELY
WATCH
WAIT
UNAVAILABLE
```

The canonical decision evaluates the economics and executability of the best available rental opportunity.

Compatibility outputs are derived from this decision, including:

- Recommendation
- Opportunity Action
- Alert Tier
- Dashboard presentation

The Opportunity Score is intentionally separate.

It measures:

> **How attractive is the current opportunity?**

The Canonical Decision answers:

> **What should the operator do?**

This distinction prevents multiple subsystems from independently determining rental guidance.

---

# System Architecture

```text
                         External APIs
                              │
                              ▼
                       Market Data Layer
                              │
                              ▼
                      Scenario Generation
                              │
                              ▼
                   Canonical Decision Engine
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
          Alert Tier    Recommendation   Opportunity
                                           Action
                              │
                              ▼
                       Persistence Layer
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
         SQLite History   JSON State    JSONL Logs
                │             │
                └──────┬──────┘
                       ▼
                 Analytics Layer
                       │
                       ▼
              Explainability Layer
                       │
                       ▼
             Dashboard / Alerts / CLI
                       │
                       ▼
                    Operator
```

The architecture is deliberately layered so that market collection, decision logic, persistence, analytics, and presentation can evolve independently.

---

# Storage and Reliability

Version 0.2 introduces a managed storage architecture designed for long-term unattended operation.

## Storage Manager

The Storage Manager is responsible for:

- Database initialization
- Database directory creation
- Schema initialization
- Schema versioning
- Schema migrations
- Integrity checking
- Startup validation
- Storage-health reporting
- Database compaction

Implementation:

```text
scripts/storage/storage_manager.py
```

---

## History Manager

The History Manager is responsible for Recommendation History operations including:

- Recording engine executions
- Retrieving historical records
- Retrieving latest values
- Historical trend windows
- History statistics
- Oldest-record pruning
- Size-based retention
- Database optimization

Implementation:

```text
scripts/storage/history_manager.py
```

---

## Schema Versioning

SQLite schema versions are tracked using:

```sql
PRAGMA user_version;
```

The migration system:

- Detects the current schema version
- Applies required migrations sequentially
- Preserves existing Recommendation History
- Updates the stored schema version
- Rejects unsupported future schema versions

This allows the database structure to evolve without requiring destructive recreation.

---

## Startup Validation

Persistent storage is validated before normal engine processing.

```text
Engine Start
    │
    ▼
Initialize Storage
    │
    ▼
Apply Migrations
    │
    ▼
Integrity Check
    │
    ▼
Healthy?
 ┌──┴──┐
 │     │
Yes    No
 │     │
 ▼     ▼
Run   Stop
Engine
```

SQLite integrity is checked using:

```sql
PRAGMA integrity_check;
```

The engine does not intentionally continue normal execution when startup storage validation fails.

---

## History Retention

Recommendation History supports automatic size-based retention.

Default maximum database size:

```text
1 GiB
```

Equivalent to:

```text
1073741824 bytes
```

When the configured maximum is exceeded, the oldest Recommendation History records are removed while preserving newer observations.

The retention limit can be changed through:

- Environment configuration
- Dashboard Settings

---

## Unlimited History

A history limit of:

```text
0
```

means:

```text
Unlimited
```

In this mode, automatic size-based pruning is disabled.

Operators using unlimited retention should monitor available disk capacity.

---

## Database Compaction

SQLite database compaction is supported using:

```sql
VACUUM;
```

Compaction may occur after pruning and can also be requested manually through the Storage dashboard.

---

# Dashboard

The Streamlit dashboard provides the primary operator interface.

Current navigation includes:

```text
Dashboard
Market
Market Trends
Strike Analysis
Pool Routing
History
Storage
Settings
```

---

## Dashboard

The main dashboard provides operator-focused decision information including:

- Current recommendation
- Canonical decision
- Opportunity Score
- Recommended strike
- Recommended pool
- Decision drivers
- Alternative strike plans
- Current blockers
- Conditions needed for stronger recommendations
- Mission timeline
- Interpretation

---

## Market

Provides current market information and BCH market visualization.

Capabilities include:

- Market metrics
- BCH candlestick charts
- Multiple time ranges
- Technical market context

---

## Market Trends

Provides historical and trend-oriented views of engine metrics.

Trend Intelligence includes:

- Direction
- Confidence
- Persistence
- Velocity
- Volatility
- Strength

---

## Strike Analysis

Provides deeper analysis of the currently recommended rental scenario.

---

## Pool Routing

Displays:

- Pool rankings
- Recommended pool
- Pool-routing information

---

## History

Provides operator access to Recommendation History and historical analytics.

---

## Storage

Provides operational visibility into the SQLite Recommendation History database.

Current information includes:

- Database size
- Configured maximum size
- Storage utilization
- History row count
- Oldest record
- Newest record
- Database health
- Integrity status
- Effective retention configuration

The page also provides a manual:

```text
Compact Database
```

control.

---

## Settings

Provides operator-facing configuration controls.

Current configurable areas include:

- Budget minimum
- Budget maximum
- Budget step
- Hashrate minimum
- Hashrate maximum
- Hashrate step
- Recommendation History retention

Settings are written to:

```text
config/dashboard_config_override.json
```

Configuration changes can request an immediate engine execution.

---

# Repository Structure

The application uses a modular repository structure.

```text
bch-rental-engine/
│
├── config/
│   ├── .env
│   ├── pools.json
│   └── dashboard_config_override.json
│
├── dashboard/
│   ├── app.py
│   ├── decision_utils.py
│   ├── frontier_data.py
│   ├── history_data.py
│   ├── market_utils.py
│   ├── settings_service.py
│   ├── ui_utils.py
│   │
│   ├── charts/
│   │
│   ├── components/
│   │
│   └── pages/
│       ├── dashboard.py
│       ├── history.py
│       ├── market.py
│       ├── market_trends.py
│       ├── pool_routing.py
│       ├── settings.py
│       ├── storage.py
│       └── strike_analysis.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── CONFIGURATION.md
│   ├── DECISION_LOG.md
│   ├── DEPLOY_EC2.md
│   ├── DEPLOYMENT_V2.md
│   ├── DEVELOPER_JOURNAL.md
│   ├── INSTALL.md
│   ├── OPERATIONS.md
│   ├── RECOMMENDATION_DECISION_MODEL.md
│   ├── RECOMMENDATION_HISTORY.md
│   ├── RELEASE_CHECKLIST.md
│   ├── ROADMAP.md
│   ├── UMBREL_MIGRATION.md
│   └── UMBREL_RELEASE_PROCESS.md
│
├── scripts/
│   ├── bch_solo_rental_strike_engine.py
│   ├── config_manager.py
│   ├── storage/
│   │   ├── history_manager.py
│   │   └── storage_manager.py
│   └── pools/
│
├── state/
├── logs/
├── tests/
│
├── Dockerfile
├── Dockerfile.dashboard
├── requirements.txt
├── run_engine.sh
└── README.md
```

The exact repository structure may continue to evolve as additional subsystems are modularized.

---

# Quick Start

## 1. Clone the Repository

```bash
git clone https://github.com/naexuis/bch-rental-engine.git
cd bch-rental-engine
```

---

## 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Create Configuration

Create:

```text
config/.env
```

Configure the required market and rental-provider settings.

For complete configuration instructions, see:

```text
docs/CONFIGURATION.md
```

---

## 5. Load Environment Variables

```bash
set -a
source config/.env
set +a
```

---

## 6. Run the Engine

The preferred module-based invocation is:

```bash
python -m scripts.bch_solo_rental_strike_engine
```

The engine will:

1. Initialize persistent storage.
2. Apply required schema migrations.
3. Validate SQLite integrity.
4. Collect current market data.
5. Generate executable rental scenarios.
6. Determine the canonical decision.
7. Calculate analytics and explanations.
8. Record Recommendation History.
9. Apply configured history retention.
10. Write current state and operational logs.

---

## 7. Run the Dashboard

```bash
streamlit run dashboard/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0
```

Then open:

```text
http://SERVER_IP:8501
```

---

# Docker

The project supports separate engine and dashboard containers.

## Build Engine

```bash
docker build \
    -t bch-rental-engine .
```

---

## Build Dashboard

```bash
docker build \
    -f Dockerfile.dashboard \
    -t bch-rental-dashboard .
```

Production deployments should persist the appropriate configuration, state, and log directories outside ephemeral container storage.

See the installation and operations documentation for the current deployment architecture.

---

# Umbrel

The BCH Rental Engine is being developed as a native Umbrel application.

The production repository convention is:

```text
~/bch_rental_engine
```

The preferred production dashboard update workflow is:

```bash
cd ~/bch_rental_engine

./scripts/update_dashboard.sh
```

Operational helper scripts include:

```text
scripts/build_dashboard.sh
scripts/deploy_dashboard.sh
scripts/restart_dashboard.sh
scripts/check_dashboard.sh
scripts/update_dashboard.sh
```

Development should not be performed directly in the production repository.

The development and production environments are intentionally separated.

Typical development repository:

```text
~/projects/bch-rental-engine
```

Typical production repository:

```text
~/bch_rental_engine
```

See:

```text
docs/UMBREL_RELEASE_PROCESS.md
docs/OPERATIONS.md
```

for the complete release and production workflow.

---

# Configuration

The application supports environment-based configuration and selected dashboard overrides.

## Configuration Precedence

For settings that support dashboard overrides:

```text
Dashboard Override
        ↓
Environment Variable
        ↓
Built-in Default
```

Dashboard overrides are stored in:

```text
config/dashboard_config_override.json
```

---

## Budget Configuration

Current budget controls include:

```text
BCH_STRIKE_BUDGET_MIN_USD
BCH_STRIKE_BUDGET_MAX_USD
BCH_STRIKE_BUDGET_STEP_USD
```

---

## Hashrate Configuration

Current hashrate controls include:

```text
BCH_HASHRATE_MIN_PH
BCH_HASHRATE_MAX_PH
BCH_HASHRATE_STEP_PH
```

---

## History Retention

Recommendation History maximum database size is configured with:

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

Set:

```text
BCH_HISTORY_MAX_SIZE_BYTES=0
```

to disable automatic size-based pruning.

---

## Runtime Paths

The application supports configurable runtime paths including:

```text
BCH_BASE_DIR
BCH_CONFIG_DIR
BCH_STATE_DIR
BCH_LOG_DIR
```

This allows the same application code to operate across:

- Development
- Docker
- Umbrel
- Other Linux deployments

For the authoritative configuration reference, see:

```text
docs/CONFIGURATION.md
```

---

# Main Outputs

By default, the application stores persistent runtime information beneath:

```text
~/bch_rental_engine/
```

Important outputs include:

## Current State

```text
~/bch_rental_engine/state/bch_solo_rental_strike_engine.json
```

Contains the most recent engine state, including:

- Market information
- Winning scenarios
- Recommendation
- Canonical decision information
- Opportunity information
- Trend analytics
- Storage health
- Effective runtime configuration
- Interpretation

---

## Recommendation History

```text
~/bch_rental_engine/state/bch_rental_history.sqlite
```

The SQLite database is the application's long-term historical intelligence store.

It supports:

- Recommendation History
- Trend Intelligence
- Historical comparisons
- Future replay
- Future forecasting
- Future strategy analysis

This database should be treated as an important persistent application asset.

---

## Engine Log

```text
~/bch_rental_engine/logs/bch_solo_rental_strike_engine.jsonl
```

---

## Alert Log

```text
~/bch_rental_engine/logs/bch_solo_rental_strike_engine_alerts.jsonl
```

JSONL logs support automatic rotation to prevent uncontrolled log-file growth.

---

# Testing

The project uses automated regression testing extensively.

The current release-hardening baseline is:

```text
251 tests
```

with the full suite passing.

Run all tests with:

```bash
pytest -q
```

Individual subsystem tests can also be executed during TDD development.

Examples:

```bash
pytest -q tests/test_storage_manager.py
```

and:

```bash
pytest -q tests/test_config_manager.py
```

---

# Development Workflow

The project follows a disciplined Test-Driven Development and release workflow.

```text
Design
   ↓
Failing Test
   ↓
Smallest Implementation
   ↓
Targeted Test
   ↓
Compilation
   ↓
Regression Testing
   ↓
Documentation
   ↓
Commit
   ↓
Push
   ↓
Runtime Validation
   ↓
Release
   ↓
Deployment
```

---

## 1. Activate the Virtual Environment

```bash
source venv/bin/activate
```

---

## 2. Load Environment Variables

```bash
set -a
source config/.env
set +a
```

---

## 3. Compile Changed Modules

For example:

```bash
python -m py_compile scripts/bch_solo_rental_strike_engine.py
```

---

## 4. Run Targeted Tests

For example:

```bash
pytest -q tests/test_storage_manager.py
```

---

## 5. Run Full Regression Suite

```bash
pytest -q
```

---

## 6. Run the Engine

```bash
python -m scripts.bch_solo_rental_strike_engine
```

---

## 7. Verify Repository State

```bash
git status
```

Feature work should be committed in logical increments.

Production releases should only be created after completing the release checklist.

See:

```text
docs/RELEASE_CHECKLIST.md
```

---

# Safety

The BCH Rental Engine is a **decision-support tool**.

It does not guarantee:

- Mining success
- Block discovery
- Profitability
- Rental availability
- Rental execution
- Future market conditions

Solo mining is inherently probabilistic.

A rental may lose the entire rental cost if no block is found.

Historical results do not guarantee future outcomes.

Before spending funds, operators should independently verify:

- Rental pricing
- Available hashrate
- Rental duration
- Pool configuration
- Pool payout details
- Wallet and payout configuration
- Network conditions
- Marketplace conditions
- Execution requirements

The application should assist human judgment, not replace it.

---

# Privacy

The BCH Rental Engine is designed as a self-hosted application.

The project should store only information required for analysis and operation.

The application should never require or intentionally collect:

- Wallet private keys
- Seed phrases
- Exchange passwords
- Personal financial credentials

API credentials should be stored securely and must never be committed to version control.

---

# Documentation

Project documentation is maintained in:

```text
docs/
```

Primary documents include:

- 📦 `INSTALL.md` — Installation Guide
- ⚙️ `CONFIGURATION.md` — Configuration Reference
- 🏗 `ARCHITECTURE.md` — Architecture Guide
- 🧠 `RECOMMENDATION_DECISION_MODEL.md` — Canonical Decision Architecture
- 📊 `RECOMMENDATION_HISTORY.md` — Historical Intelligence Architecture
- 🛠 `OPERATIONS.md` — Operations Runbook
- ☂️ `UMBREL_RELEASE_PROCESS.md` — Umbrel Release Process
- 🗺 `ROADMAP.md` — Development Roadmap
- ✅ `RELEASE_CHECKLIST.md` — Release Validation Checklist
- 📝 `CHANGELOG.md` — Release History
- 📔 `DEVELOPER_JOURNAL.md` — Engineering Journal
- 💡 `DECISION_LOG.md` — Architectural Decision Log

Each major subsystem should have a clear authoritative document.

---

# Roadmap

## v0.1 — Foundation

**Status:** Complete

Established:

- Core rental engine
- Canonical decision architecture
- Opportunity Score
- Recommendation History
- Trend Intelligence
- Explainability
- Dashboard
- Pool routing
- Notifications
- Native Umbrel foundation

---

## v0.2 — Storage & Reliability

**Status:** Release Hardening

Adds:

- Storage Manager
- History Manager
- Schema versioning
- Schema migrations
- Database integrity checks
- Startup validation
- History retention
- Database optimization
- Storage-health reporting
- Storage dashboard
- Runtime configuration manager
- Dashboard retention controls

---

## v0.3 — System Intelligence

Planned focus:

- Engine Health
- API Health
- Pricing Source Health
- Rental Source Health
- Startup Diagnostics
- Automatic Recovery
- Background Task Monitoring
- Self-Test Framework

---

## v0.4 — Forecast Intelligence

Planned focus:

- Trend acceleration
- Trend deceleration
- Trend reversal detection
- Plateau detection
- Forecast confidence
- Strike probability forecasting
- Time-to-strike estimation

---

## v0.5 — Historical Intelligence

Planned focus:

- Historical ROI analysis
- Historical FVR analysis
- Recommendation frequency
- Market-regime statistics
- Opportunity Score distributions
- Long-term analytics

---

## v0.6 — Operator Experience

Planned focus:

- First-run setup wizard
- Guided configuration
- Improved dashboard layouts
- Mobile-friendly views
- Export history
- Historical playback

---

## v0.7 — Automation

Planned focus:

- Scheduled reports
- Notification improvements
- Discord
- Email
- Webhooks
- Daily market summaries
- Automatic diagnostics

---

## v0.8 — Strategy Lab

Planned focus:

- Historical replay
- Strategy simulation
- Parameter optimization
- Profitability comparison
- What-if analysis
- Strike replay

---

## v0.9 — Multi-Coin Platform

Planned expansion beyond Bitcoin Cash.

Potential networks include:

- Bitcoin
- Litecoin
- Dogecoin
- Kaspa
- Monero
- Additional SHA-256-compatible networks

---

## v1.0 — BCH Rental Intelligence Platform

Long-term objective:

A mature, reliable, explainable, historically aware, self-monitoring, extensively tested, and production-ready rental intelligence platform.

---

# Guiding Principles

Every feature should improve one or more of the following:

## Recommendation Quality

Produce more useful and actionable rental recommendations.

## Explainability

Every recommendation should clearly explain why it was generated.

## Reliability

The engine should operate unattended for extended periods and fail safely when critical systems are unhealthy.

## Historical Intelligence

Historical data should improve understanding of how opportunities evolve over time.

## Operator Experience

Complex mining analytics should be presented through a clear and intuitive interface.

## Maintainability

Architecture should remain modular, well-tested, and easy to extend.

## Performance

Execution time, storage efficiency, and resource utilization should remain appropriate for self-hosted environments.

## Privacy

Only information required for analysis and operation should be stored.

---

# Long-Term Vision

The BCH Rental Engine has evolved from a probability and profitability calculator into an explainable mining decision-support platform.

Future development will continue focusing on:

- Better recommendations
- Better explanations
- Better historical intelligence
- Better forecasting
- Better reliability
- Better operational visibility
- Better operator experience

The long-term objective is not to build a system that claims to predict mining outcomes perfectly.

It is to build a system that operators can trust because every recommendation is:

- Transparent
- Explainable
- Reproducible
- Testable
- Historically traceable
- Operationally actionable
- Backed by measurable evidence