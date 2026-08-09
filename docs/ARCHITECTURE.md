# BCH Rental Engine
# Architecture Guide

**Architecture Revision:** 4.0

**Application Release:** 0.2.x

**Architecture Status:** Stable — Canonical Decision + Storage & Reliability Architecture

---

# Purpose

The BCH Rental Engine is an explainable decision-support platform for evaluating Bitcoin Cash solo-mining hashpower rental opportunities.

Unlike a traditional mining calculator that produces only a profitability estimate, the BCH Rental Engine continuously evaluates market conditions, generates executable rental scenarios, determines a single canonical operator decision, explains the reasoning behind that decision, records historical observations, evaluates trends, manages its persistent storage, and presents actionable guidance through an operator dashboard.

The guiding philosophy of the project is:

> **Every recommendation should be transparent, explainable, reproducible, testable, historically traceable, and backed by measurable evidence.**

The engine is designed to answer five fundamental questions:

- Should I rent hashpower?
- Why was that recommendation made?
- What changed since the last analysis?
- What must improve before a stronger recommendation can be made?
- Is the system itself healthy enough for the recommendation to be trusted?

---

# Architecture Goals

The architecture is designed to provide:

- Explainable recommendations
- One authoritative decision model
- Historical traceability
- Reliable long-term operation
- Safe schema evolution
- Controlled storage growth
- Operator visibility
- Modular development
- Testable subsystems
- Portable deployment
- Backward compatibility

The system should remain understandable even as new analytics and operational capabilities are added.

---

# Design Principles

The BCH Rental Engine is built around ten architectural principles.

---

# 1. Single Source of Truth

Business decisions are made exactly once.

The engine contains a single:

```text
Canonical Decision Engine
```

that determines the operator recommendation.

Current canonical outputs include:

- Canonical Decision
- Alert Tier
- Recommendation
- Opportunity Action
- Dashboard decision presentation

Downstream layers consume or derive information from the canonical decision rather than independently deciding whether a rental should occur.

This prevents contradictory recommendation systems from emerging across the application.

---

# 2. Explainability

Operators should never be required to trust a black box.

Every recommendation should be explainable using measurable inputs such as:

- Canonical Decision
- Opportunity Score
- Fair Value Ratio
- Risk-adjusted ROI
- Probability
- Market Regime
- Historical trends
- Decision blockers
- Rental economics
- Current system state

The Explainability Layer is responsible for translating quantitative conditions into operator-facing reasoning.

---

# 3. Separation of Responsibilities

Each subsystem owns one architectural responsibility.

```text
Market Data
    ↓
Scenario Generation
    ↓
Canonical Decision
    ↓
Persistence
    ↓
Historical Analytics
    ↓
Explainability
    ↓
Presentation
    ↓
Operator
```

Operational services such as configuration and storage management support these layers without becoming alternate decision systems.

---

# 4. Test-Driven Development

Every architectural change follows the same engineering workflow.

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

Behavioral changes are normally introduced through failing tests first.

Refactors are protected by regression tests before internal structure is changed.

---

# 5. Portability

The same application code is designed to operate across multiple environments.

Supported or documented environments include:

- Native Umbrel
- Docker
- Ubuntu
- Local Linux development
- Raspberry Pi-class systems
- AWS
- Other Linux container hosts

Runtime paths are configurable so deployment-specific filesystem layouts do not need to be hardcoded into application logic.

---

# 6. Backward Compatibility

Architectural improvements should preserve existing user data and downstream interfaces whenever practical.

Examples include:

- Legacy recommendation compatibility
- Legacy SQLite schema migration
- Historical row preservation during database upgrades
- Compatibility mappings from older recommendation terminology
- Existing dashboard state compatibility

The system favors migration over destructive replacement.

---

# 7. Explainable Intelligence

Analytics should improve operator understanding rather than replace operator judgment.

The engine is intentionally a:

```text
Decision-Support Platform
```

not an autonomous rental execution system.

Statistical probability does not eliminate mining risk.

Recommendations must remain traceable to observable data and documented rules.

---

# 8. Storage Is a First-Class Subsystem

Recommendation History is not treated as a side effect of engine execution.

It is a production subsystem with responsibility for:

- Database initialization
- Schema management
- Historical persistence
- Integrity validation
- Storage statistics
- Retention
- Compaction
- Operational health

Historical observations cannot be recreated retroactively if they are lost.

Storage therefore receives explicit architectural protection.

---

# 9. Configuration Must Be Observable

The configuration an operator sees should match the configuration the engine actually uses.

For dashboard-supported settings, resolution follows:

```text
Dashboard Override
        ↓
Environment Variable
        ↓
Built-in Default
```

The effective resolved configuration is published in the latest engine state so the dashboard can report runtime truth rather than static defaults.

---

# 10. Presentation Contains No Core Decision Logic

Dashboard pages, charts, notification renderers, and CLI output should consume engine state rather than reproduce business logic.

Presentation modules may:

- Format values
- Display metrics
- Visualize trends
- Explain decisions
- Trigger supported configuration actions

They should not independently determine whether the operator should rent hashpower.

---

# High-Level Architecture

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
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
        Alert Tier      Recommendation   Opportunity Action
                              │
                              ▼
                     Persistence Layer
          ┌───────────────────┼────────────────────┐
          ▼                   ▼                    ▼
    SQLite History        JSON State          JSONL Logs
          │                   │
          ▼                   │
 Historical Analytics        │
          │                   │
          └──────────┬────────┘
                     ▼
               Explainability
                     │
                     ▼
        Dashboard • CLI • Notifications
                     │
                     ▼
                  Operator
```

Supporting operational subsystems:

```text
Configuration Manager
        │
        ├── Dashboard overrides
        ├── Environment variables
        └── Built-in defaults

Storage Manager
        │
        ├── Database initialization
        ├── Schema versioning
        ├── Schema migration
        ├── Integrity checks
        └── Startup validation

History Manager
        │
        ├── Row insertion
        ├── History retrieval
        ├── Trend windows
        ├── Storage statistics
        ├── History pruning
        └── Size retention
```

---

# Repository Structure

```text
bch-rental-engine/

├── config/
│   ├── dashboard_config_override.json
│   ├── pools.json
│   └── ...
│
├── dashboard/
│   ├── app.py
│   ├── charts/
│   ├── components/
│   ├── pages/
│   ├── decision_utils.py
│   ├── frontier_data.py
│   ├── history_data.py
│   ├── market_utils.py
│   ├── settings_service.py
│   └── ui_utils.py
│
├── docs/
│
├── logs/
│
├── scripts/
│   ├── bch_solo_rental_strike_engine.py
│   ├── config_manager.py
│   └── storage/
│       ├── history_manager.py
│       └── storage_manager.py
│
├── state/
│   ├── bch_solo_rental_strike_engine.json
│   └── bch_rental_history.sqlite
│
├── tests/
│
├── Dockerfile
├── Dockerfile.dashboard
└── docker-compose.yml
```

The repository is structured so that decision logic, persistence, operational services, analytics, and presentation can evolve independently.

---

# Architectural Layers

---

# Layer 1 — Market Data

Purpose:

Collect the current Bitcoin Cash mining and rental environment.

Current data sources and inputs include:

- BCH market pricing
- BTC market pricing
- BCH network difficulty
- BCH network hashrate
- Braiins rental pricing
- MiningRigRentals pricing
- Rental availability
- Pool information

Typical outputs include:

- BTC/USD
- BCH/USD
- BCH/BTC
- Network difficulty
- Estimated network hashrate
- Rental price
- Available rental hashrate

Market Data provides inputs.

It does not make operator decisions.

---

# Layer 2 — Scenario Generation

Purpose:

Generate executable rental scenarios within configured operational constraints.

Each candidate scenario evaluates factors such as:

- Budget
- Rental source
- Rental hashrate
- Rental duration
- Rental cost
- Expected blocks
- Probability of at least one block
- Probability of multiple blocks
- Expected revenue
- Expected profit
- ROI
- Risk-adjusted ROI
- Fair Value Ratio
- Premium or discount
- Execution constraints

Only scenarios considered executable continue into recommendation evaluation.

---

# Layer 3 — Canonical Decision Engine

The Canonical Decision Engine is the authoritative operator-decision layer.

Every operator recommendation originates from the canonical decision architecture.

The core decision function is:

```text
determine_canonical_decision()
```

Current canonical states include:

```text
RENT_NOW

READY

WATCH_CLOSELY

WATCH

WAIT

UNAVAILABLE
```

The Canonical Decision Engine evaluates conditions including:

- Scenario executability
- Fair Value Ratio
- Risk-adjusted ROI
- Probability thresholds
- Economic conditions

No dashboard page, notification path, or analytics subsystem independently decides whether the operator should rent.

For detailed decision-model documentation, see:

```text
docs/RECOMMENDATION_DECISION_MODEL.md
```

---

# Layer 4 — Compatibility Layer

Some historical interfaces predate the Canonical Decision architecture.

Compatibility outputs include:

- Recommendation
- Alert Tier
- Opportunity Action

These values remain supported so existing:

- State files
- Historical records
- Tests
- Dashboard views
- Notifications

can continue functioning during architectural evolution.

Compatibility logic should remain thin and derive from canonical state whenever possible.

---

# Layer 5 — Opportunity Scoring

The Opportunity Score measures:

```text
Opportunity Attractiveness
```

It does not directly determine operator guidance.

Inputs may include:

- Fair Value Ratio
- Probability
- Risk-adjusted ROI
- Market Regime
- Other documented scoring signals

Output:

```text
Opportunity Score
```

The score helps explain relative opportunity quality.

The final recommendation remains the responsibility of the Canonical Decision Engine.

---

# Layer 6 — Persistence

The engine maintains three persistent output types.

```text
SQLite
JSON
JSONL
```

Each serves a distinct purpose.

---

## SQLite — Recommendation History

Primary historical database:

```text
state/bch_rental_history.sqlite
```

SQLite stores long-term engine execution history.

Historical fields include information such as:

- Timestamp
- Market values
- Rental source
- Rental economics
- Probability
- Expected profit
- ROI
- Risk-adjusted ROI
- Fair Value Ratio
- Recommendation
- Opportunity Score
- Opportunity Action
- Canonical Decision
- Budget configuration
- Rental-source pricing

Recommendation History provides the evidence used by historical analytics.

---

## JSON — Current State

Current engine state is stored in:

```text
state/bch_solo_rental_strike_engine.json
```

The state represents the latest completed engine execution.

It includes information such as:

- Market state
- Scenario winners
- Recommendation
- Canonical decision
- Opportunity state
- Trend analytics
- Pool routing
- Frontier information
- Interpretation
- Effective configuration
- Storage health

The dashboard primarily consumes this current-state representation together with historical SQLite data.

---

## JSONL — Operational Logs

Operational execution logs are written as append-only JSONL.

Typical files include:

```text
logs/bch_solo_rental_strike_engine.jsonl
logs/bch_solo_rental_strike_engine_alerts.jsonl
```

JSONL provides:

- Execution records
- Error diagnostics
- Alert records
- Operational troubleshooting information

Logs are operational records rather than analytical history.

---

# Storage Architecture

Version 0.2 introduces storage as an explicit production subsystem.

The storage architecture is divided into:

```text
Storage Manager
        +
History Manager
```

These modules separate database lifecycle management from historical data operations.

---

# Storage Manager

Implementation:

```text
scripts/storage/storage_manager.py
```

The Storage Manager owns database lifecycle and health.

Responsibilities include:

- Automatic database creation
- Parent-directory creation
- Schema initialization
- Schema versioning
- Sequential schema migration
- Future-schema rejection
- Database size reporting
- Row-count reporting
- SQLite integrity checking
- Database compaction
- Storage health reporting
- Startup validation

---

# Self-Initializing Database

The history database is self-initializing.

When the database does not exist:

```text
initialize_history_database()
```

creates:

- Required parent directories
- SQLite database
- `run_history` table
- Current schema

Manual database initialization is not required during normal operation.

---

# Schema Versioning

SQLite schema version is tracked using:

```sql
PRAGMA user_version;
```

The application defines:

```text
CURRENT_SCHEMA_VERSION
```

which represents the schema supported by the running application.

This makes database structure explicit rather than inferring version solely from the presence of columns.

---

# Sequential Schema Migrations

Schema upgrades are applied through:

```text
apply_schema_migrations()
```

Migration flow:

```text
Current Database Version
        ↓
Required Migration
        ↓
Next Version
        ↓
Required Migration
        ↓
CURRENT_SCHEMA_VERSION
```

The current architecture includes an explicit legacy migration:

```text
migrate_schema_v0_to_v1()
```

This migration adds missing version-1 fields while preserving existing rows.

Future migrations should follow the same ordered model:

```text
v1 → v2 → v3 → ...
```

rather than using one monolithic migration block.

---

# Legacy Database Preservation

Legacy version-0 databases are upgraded in place.

Migration preserves:

- Existing history rows
- Existing timestamps
- Existing opportunity fields
- Existing identifiers

New fields may initially contain:

```text
NULL
```

where no historical value existed before the schema upgrade.

Historical data should not be discarded merely because the schema changes.

---

# Future-Schema Protection

If a database reports a schema version newer than the running application supports, initialization raises an error.

Example:

```text
Database schema version: 2
Application supports: 1
```

The older application does not silently downgrade the database.

This prevents accidental corruption when an older binary is started against data created by a newer release.

---

# Database Integrity

Database integrity is checked with SQLite:

```sql
PRAGMA integrity_check;
```

Healthy result:

```text
ok
```

The application exposes:

```text
check_database_integrity()
```

for storage health evaluation.

---

# Startup Storage Validation

The engine performs storage validation before normal decision processing.

Function:

```text
validate_storage_startup()
```

Startup sequence:

```text
Application Start
        ↓
Initialize Database
        ↓
Apply Schema Migrations
        ↓
Check SQLite Integrity
        ↓
Healthy?
   ┌────┴────┐
   │         │
  Yes        No
   │         │
   ▼         ▼
Run Engine   Raise Error
```

This prevents the engine from continuing normal operation against storage that fails integrity validation.

---

# Storage Health Model

Storage health is represented by:

```text
StorageHealth
```

Current health attributes include:

- `database_exists`
- `database_size_bytes`
- `row_count`
- `integrity_ok`

Storage health is published into the engine's latest state so operational surfaces can inspect database condition.

---

# History Manager

Implementation:

```text
scripts/storage/history_manager.py
```

The History Manager owns Recommendation History operations.

Responsibilities include:

- Insert history rows
- Retrieve recent history
- Retrieve latest values
- Build analytical trend windows
- Calculate history statistics
- Delete oldest history rows
- Enforce size-based retention

This separates historical data behavior from low-level database lifecycle management.

---

# History Recording

Each successful engine execution records a history row.

Typical flow:

```text
Engine Execution
        ↓
Recommendation Generated
        ↓
insert_history_row()
        ↓
SQLite Recommendation History
```

History recording supports:

- Historical analytics
- Trend Intelligence
- Recommendation comparisons
- Future replay
- Future strategy research

---

# History Statistics

The History Manager provides a unified storage statistics API.

Current statistics include:

- Record count
- Oldest timestamp
- Newest timestamp
- Database size

These values support both operational retention logic and the dashboard Storage page.

---

# History Retention

The database supports configurable size-based retention.

Configuration key:

```text
history_max_size_bytes
```

Environment fallback:

```text
BCH_HISTORY_MAX_SIZE_BYTES
```

Default:

```text
1073741824 bytes
```

Equivalent to:

```text
1 GiB
```

---

# Retention Flow

After a successful history insert:

```text
Insert History Row
        ↓
Check Configured Size Limit
        ↓
Database Under Limit?
    ┌───────┴────────┐
    │                │
   Yes               No
    │                │
    ▼                ▼
 Continue       Prune Oldest Rows
                     ↓
                  VACUUM
                     ↓
                Recheck Size
```

Newest observations are preserved preferentially.

---

# Oldest-Row Pruning

Low-level pruning is handled by:

```text
prune_oldest_history_rows()
```

The function:

- Deletes the oldest rows first
- Deletes no more than requested
- Handles requests larger than available history
- Performs no work for zero or negative row counts
- Returns the actual number of rows removed

This primitive is intentionally separate from policy decisions.

---

# Size-Limit Enforcement

Policy is implemented by:

```text
enforce_history_size_limit()
```

Behavior:

- Does nothing when under the configured limit
- Removes oldest history when over the limit
- Deletes history in controlled batches
- Compacts SQLite after pruning
- Rechecks physical file size
- Stops safely if no history remains
- Avoids infinite loops for impossible size targets

An SQLite database has a minimum physical size even when empty, so the retention system must not assume every configured byte limit can literally be reached.

---

# Unlimited History

A configured history size of:

```text
0
```

means:

```text
Unlimited
```

In unlimited mode:

- Automatic size-based pruning is skipped
- Recommendation History can grow indefinitely
- Disk usage must be monitored externally

Unlimited mode is supported intentionally rather than being treated as an invalid value.

---

# Database Compaction

SQLite row deletion does not necessarily shrink the physical database file.

Therefore the system supports:

```text
VACUUM
```

through:

```text
vacuum_database()
```

Compaction is used to reclaim unused database pages.

Current use cases include:

- Automatic retention cleanup
- Manual operator maintenance

---

# Configuration Architecture

Configuration is centralized through:

```text
scripts/config_manager.py
```

The configuration manager separates resolution logic from the main engine module.

---

# Configuration Sources

Supported sources include:

```text
Dashboard Override
Environment Variables
Built-in Defaults
```

For supported settings, precedence is:

```text
Dashboard Override
        ↓
Environment Variable
        ↓
Built-in Default
```

---

# Dashboard Override

Dashboard-controlled configuration is persisted in:

```text
config/dashboard_config_override.json
```

Current configurable values include:

- Budget minimum
- Budget maximum
- Budget step
- Hashrate minimum
- Hashrate maximum
- Hashrate step
- History maximum size

The Settings page writes this file.

---

# Effective Runtime Configuration

The engine publishes the resolved configuration in:

```text
state/bch_solo_rental_strike_engine.json
```

under:

```text
config
```

This ensures the dashboard can display what the engine actually used.

Example:

```text
Environment says:       2 GiB
Dashboard override:     none
Effective state:        2 GiB
Storage page displays:  2 GiB
```

Operational interfaces should prefer effective runtime state over assumptions about configuration sources.

---

# Layer 7 — Historical Analytics

Recommendation History is converted into reusable analytical primitives.

Current capabilities include:

- Recent history retrieval
- Latest metric retrieval
- Historical trend windows
- Numeric trend calculation
- Direction
- Confidence
- Persistence
- Velocity
- Volatility
- Trend Strength
- Opportunity Score changes
- Recommendation changes

Analytics functions are intentionally separated from database access.

Conceptually:

```text
SQLite History
      ↓
History Retrieval
      ↓
Numeric Analytics
      ↓
Interpretation
```

---

# Layer 8 — Explainability

Purpose:

Transform engine state and historical analytics into operator-facing explanations.

Current explanation areas include:

- Recommendation reasoning
- Opportunity history
- Trend direction
- Trend strength
- Score limiters
- Economic blockers
- Conditions required for a stronger recommendation

The Explainability Layer answers questions such as:

- What changed?
- Why did the recommendation change?
- What is preventing RENT?
- Which conditions are improving?
- Which conditions are deteriorating?
- How strong is the current trend?

Explainability consumes decision and analytical outputs.

It does not replace the Canonical Decision Engine.

---

# Layer 9 — Presentation

Presentation surfaces consume engine state and historical analytics.

Current surfaces include:

- Streamlit Dashboard
- Command Line Interface
- Telegram alerts

Future presentation integrations may include:

- Discord
- Email
- Scheduled reports
- Webhooks

Presentation code should contain minimal domain logic.

---

# Dashboard Architecture

The dashboard has been refactored from a large monolithic application into modular page, component, chart, data, and utility layers.

Primary entry point:

```text
dashboard/app.py
```

The application entry point is responsible mainly for:

- Runtime path resolution
- Current state loading
- History loading
- Navigation
- Shared context
- Page routing

Page-specific rendering lives outside `app.py`.

---

# Dashboard Page Architecture

Current page modules include:

```text
dashboard/pages/dashboard.py
dashboard/pages/market.py
dashboard/pages/market_trends.py
dashboard/pages/strike_analysis.py
dashboard/pages/pool_routing.py
dashboard/pages/history.py
dashboard/pages/storage.py
dashboard/pages/settings.py
```

Navigation flow:

```text
dashboard/app.py
        ↓
Selected Page
        ↓
dashboard/pages/<page>.py
```

This keeps page-specific Streamlit rendering isolated.

---

# Dashboard Components

Reusable visual blocks live under:

```text
dashboard/components/
```

Examples include:

- Mission timeline
- Pool recommendation
- Alternative strike plans
- Pool routing helpers

Components receive structured data and render reusable UI sections.

---

# Dashboard Charts

Chart-building logic lives under:

```text
dashboard/charts/
```

Separating charts from page routing reduces coupling between visualization behavior and application navigation.

---

# Dashboard Utility Layer

Shared display and calculation helpers live in modules such as:

```text
dashboard/ui_utils.py
dashboard/decision_utils.py
dashboard/market_utils.py
dashboard/frontier_data.py
dashboard/history_data.py
dashboard/settings_service.py
```

Examples include:

- Safe numeric handling
- Hashrate formatting
- Large-number formatting
- Progress calculations
- Probability curves
- Decision compatibility mapping
- Market technical indicators
- Frontier normalization
- SQLite history loading
- Settings persistence

---

# Storage Dashboard

The Storage page is implemented in:

```text
dashboard/pages/storage.py
```

It displays:

- Current database size
- Configured retention limit
- Storage utilization
- History record count
- Oldest record
- Newest record
- Database health
- Integrity status

It also provides:

```text
Compact Database
```

for manual SQLite maintenance.

The page consumes storage APIs rather than directly implementing database policy.

---

# Settings Dashboard

The Settings page is implemented in:

```text
dashboard/pages/settings.py
```

It supports operator-controlled settings such as:

- Budget range
- Hashrate range
- History retention

The UI presents storage retention in:

```text
GiB
```

while the engine configuration contract remains:

```text
bytes
```

The conversion is presentation-specific.

The canonical stored value remains:

```text
history_max_size_bytes
```

---

# Immediate-Run Trigger

Saving dashboard configuration can request an immediate engine run.

Trigger file:

```text
config/run_now.trigger
```

The production launcher detects this trigger and initiates execution.

This allows configuration changes to become active without requiring manual command execution.

---

# Current Data Flow

```text
External APIs
      │
      ▼
Market Data
      │
      ▼
Scenario Generation
      │
      ▼
Canonical Decision Engine
      │
      ├────────► Alert Tier
      ├────────► Recommendation
      └────────► Opportunity Action
      │
      ▼
Persistence
      │
      ├────────► SQLite History
      ├────────► JSON State
      └────────► JSONL Logs
      │
      ▼
Historical Analytics
      │
      ▼
Explainability
      │
      ▼
Dashboard / CLI / Notifications
```

Operational side flow:

```text
Dashboard Settings
      │
      ▼
dashboard_config_override.json
      │
      ▼
Configuration Manager
      │
      ▼
Effective Engine Configuration
      │
      ▼
Latest State
      │
      ▼
Dashboard
```

Storage lifecycle:

```text
Engine Startup
      │
      ▼
Storage Initialization
      │
      ▼
Schema Migration
      │
      ▼
Integrity Validation
      │
      ▼
Engine Execution
      │
      ▼
History Insert
      │
      ▼
Retention Enforcement
```

---

# Testing Architecture

The BCH Rental Engine uses layered automated testing.

Current regression coverage includes:

- Recommendation logic
- Canonical decision compatibility
- Opportunity scoring
- Recommendation History
- Trend Intelligence
- Interpretation
- Storage Manager
- History Manager
- Schema versioning
- Schema migrations
- Future-schema protection
- Startup storage validation
- Storage statistics
- History pruning
- Retention policy
- Engine configuration
- Dashboard configuration
- Dashboard decision utilities
- Dashboard UI utilities
- Frontier data
- History data
- Market utilities
- Yahoo Finance normalization
- Probability curves
- Launcher behavior
- Path behavior

At the completion of the Version 0.2 Storage & Reliability development work, the full suite contains:

```text
259 automated tests
```

The test count is not itself the objective.

The architectural goal is to protect behavioral contracts at subsystem boundaries.

---

# Test Boundaries

Testing is intentionally concentrated on:

```text
Decision Logic
Data Transformation
Persistence
Configuration
Analytics
Migration
Retention
Operational Safety
```

Streamlit rendering code receives lighter direct unit testing because presentation-specific tests can become brittle.

Reusable logic is extracted from presentation code wherever practical so it can be tested independently.

---

# Release Architecture

Current production delivery is built around the native Umbrel application workflow.

Conceptual release flow:

```text
Development Repository
        │
        ▼
Feature Branch
        │
        ▼
Regression Verification
        │
        ▼
Release Commit
        │
        ▼
Git Tag
        │
        ▼
Container Build
        │
        ▼
Umbrel Deployment
        │
        ▼
Production Validation
```

Production update helpers manage common deployment tasks.

The detailed procedure is documented in:

```text
docs/UMBREL_RELEASE_PROCESS.md
```

---

# Deployment Architecture

Production separates application code from persistent operational data.

Persistent data includes:

```text
config/
state/
logs/
```

Replaceable application assets include:

- Engine source
- Dashboard source
- Container images

Deployment should never require deleting Recommendation History.

---

# Failure Domains

The architecture intentionally isolates several major failure domains.

---

## Market Data Failure

Examples:

- API unavailable
- Provider timeout
- Invalid pricing response

Handled by provider/network logic.

Should not corrupt persistence.

---

## Decision Failure

Examples:

- No executable scenario
- Insufficient opportunity conditions

Produces a valid non-rental state rather than a storage failure.

---

## Storage Failure

Examples:

- Unsupported future schema
- Integrity failure
- Unwritable database
- Disk exhaustion

Should stop or constrain engine operation rather than silently lose history.

---

## Dashboard Failure

A dashboard rendering error should not modify decision history or recommendation logic.

The engine and dashboard remain separate operational components.

---

## Configuration Failure

Malformed dashboard configuration falls back safely where supported.

Secrets and deployment-specific defaults remain environment-controlled.

---

# Documentation Map

The BCH Rental Engine documentation is organized into focused documents.

| Document | Purpose |
|----------|---------|
| **ARCHITECTURE.md** | High-level system and subsystem architecture |
| **RECOMMENDATION_DECISION_MODEL.md** | Canonical Decision Engine design |
| **RECOMMENDATION_HISTORY.md** | Historical recommendation model |
| **CONFIGURATION.md** | Runtime and dashboard configuration |
| **OPERATIONS.md** | Day-to-day production operations |
| **RELEASE_CHECKLIST.md** | Pre-release and production verification |
| **UMBREL_RELEASE_PROCESS.md** | Umbrel release workflow |
| **INSTALL.md** | Installation instructions |
| **ROADMAP.md** | Development milestones |
| **CHANGELOG.md** | Release history |
| **DECISION_LOG.md** | Major architectural decisions |
| **DEVELOPER_JOURNAL.md** | Development history and engineering notes |

Each subsystem should have one authoritative source where practical.

`ARCHITECTURE.md` serves as the high-level entry point into the system design.

---

# Current Architecture Status

The current architecture includes:

- ✅ Market Data Layer
- ✅ Scenario Generation
- ✅ Canonical Decision Engine
- ✅ Compatibility Layer
- ✅ Opportunity Scoring
- ✅ SQLite Recommendation History
- ✅ Current JSON State
- ✅ JSONL Operational Logging
- ✅ Historical Analytics
- ✅ Trend Intelligence
- ✅ Explainability
- ✅ Configuration Manager
- ✅ Storage Manager
- ✅ History Manager
- ✅ Self-initializing database
- ✅ Explicit schema versioning
- ✅ Sequential schema migration
- ✅ Future-schema protection
- ✅ Database integrity checks
- ✅ Startup storage validation
- ✅ Storage health model
- ✅ Size-based history retention
- ✅ Unlimited-history mode
- ✅ SQLite compaction
- ✅ Modular Streamlit dashboard
- ✅ History dashboard
- ✅ Storage dashboard
- ✅ Settings dashboard
- ✅ Native Umbrel deployment
- ✅ Expanded automated regression suite

The Version 0.2 Storage & Reliability architecture has been production validated.

---

# Architecture Evolution

The architecture has evolved through several major stages.

```text
Probability Calculator
        ↓
Rental Scenario Engine
        ↓
Recommendation Engine
        ↓
Historical Decision Platform
        ↓
Canonical Decision Architecture
        ↓
Trend Intelligence
        ↓
Modular Dashboard
        ↓
Production Storage Architecture
```

Each stage extended existing layers rather than replacing the entire system.

This incremental approach is a deliberate architectural strategy.

---

# Version 0.2 Architectural Contribution

Version 0.2 primarily strengthens:

```text
Persistence
Reliability
Maintainability
Operator Visibility
```

Major additions include:

- Storage lifecycle abstraction
- History lifecycle abstraction
- Explicit schema management
- Ordered migration architecture
- Startup database validation
- Controlled storage growth
- Operator-controlled retention
- Storage health reporting
- Dedicated Storage dashboard
- Configuration extraction
- Modular dashboard structure
- Expanded regression protection

This version intentionally focuses on operational reliability rather than adding new recommendation intelligence.

---

# Next Architecture Milestone

The next planned milestone is:

```text
Version 0.3 — System Intelligence
```

Expected architectural additions include:

- Engine Health
- API Health
- Pricing Source Status
- Rental Source Status
- Database Health expansion
- Startup Diagnostics
- Background Task Monitoring
- Automatic Recovery
- Self-Test Framework

These capabilities should build on the storage-health and startup-validation primitives introduced in Version 0.2.

---

# Future Architecture

Longer-term planned additions include:

## System Intelligence

```text
Version 0.3
```

- Service health model
- Provider health
- Recovery behavior
- Diagnostics
- Self-tests

---

## Forecast Intelligence

```text
Version 0.4
```

- Trend acceleration
- Trend deceleration
- Trend reversal
- Plateau detection
- Forecast confidence
- Strike probability forecasting
- Time-to-strike estimation

---

## Historical Intelligence

```text
Version 0.5
```

- Historical ROI analysis
- Historical FVR analysis
- Recommendation frequency
- Regime statistics
- Opportunity Score distributions
- Long-term analytics

---

## Operator Experience

```text
Version 0.6
```

- First-run setup
- Guided configuration
- Expanded storage management
- Dashboard customization
- Historical exports
- Historical playback

---

## Automation

```text
Version 0.7
```

- Scheduled reports
- Notification expansion
- Daily summaries
- Automatic diagnostics

---

## Strategy Lab

```text
Version 0.8
```

- Historical replay
- Strategy simulation
- Parameter optimization
- What-if analysis

---

## Multi-Coin Architecture

```text
Version 0.9
```

The existing layered architecture should eventually be generalized so market-data providers, mining economics, and network assumptions can vary by coin without duplicating the decision-support framework.

---

# Architectural Constraints

Future development should preserve these constraints.

## One Canonical Decision

Do not introduce parallel recommendation engines.

---

## One Storage Lifecycle

Schema initialization, migration, integrity validation, and storage health should remain centralized.

---

## One Historical Data Contract

Recommendation History should evolve through versioned migration rather than ad hoc destructive changes.

---

## One Configuration Resolution Model

Supported configuration should follow explicit precedence rules.

---

## Presentation Is Not Business Logic

Do not move recommendation logic into Streamlit pages, charts, or notifications.

---

## Historical Data Is Valuable

Do not delete, reset, or rebuild Recommendation History as a routine migration strategy.

---

## Tests Protect Contracts

Refactors should preserve externally observable behavior unless a behavioral change is intentionally documented.

---

# Long-Term Vision

The BCH Rental Engine has evolved from a mining probability calculator into a modular, historically aware, operationally reliable decision-support platform.

The long-term objective is to build a system operators trust because every recommendation is:

- Transparent
- Explainable
- Reproducible
- Testable
- Historically traceable
- Operationally observable
- Storage-aware
- Actionable

Future development should continue emphasizing:

- Simplicity
- Modularity
- Architectural consistency
- Explainable analytics
- Historical intelligence
- Decision quality
- Operational reliability
- Safe evolution

Every new capability should strengthen the existing architecture rather than create parallel systems.

---

# Architectural Principle

The BCH Rental Engine should become more capable without becoming less understandable.

The preferred architecture is therefore:

```text
One Decision Model
+
Clear Subsystems
+
Versioned Storage
+
Observable Configuration
+
Historical Evidence
+
Explainable Analytics
+
Thin Presentation Layers
+
Automated Regression Protection
```

That combination provides the foundation for the long-term BCH Rental Intelligence Platform.