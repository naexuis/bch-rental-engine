# BCH Rental Engine Roadmap

The BCH Rental Engine is an open-source decision-support platform for evaluating Bitcoin Cash (BCH) hashpower rental opportunities.

Rather than attempting to predict the future with a black-box algorithm, the engine provides transparent, explainable, and data-driven recommendations that help operators answer one central question:

> **"Should I rent hashpower right now?"**

The long-term vision is to build a trusted, historically aware, operationally reliable analytics platform for cryptocurrency hashpower rentals.

The objective is not to automate mining decisions.

The objective is to explain them.

---

# Current Version

**Version:** v0.2.x

**Status:** Release Hardening

**Platform:** Native Umbrel Application

**Current Milestone:** Storage & Reliability

---

# Project Vision

The BCH Rental Engine combines:

- Live market pricing
- BCH network conditions
- Rental marketplace pricing
- Statistical probability
- Risk-adjusted profitability
- Opportunity scoring
- Canonical decision logic
- Recommendation explainability
- Historical analytics
- Trend Intelligence
- Storage management
- Operational monitoring
- System health foundations

Every recommendation should help the operator understand:

- Should I rent?
- Why?
- What changed?
- What is preventing a stronger recommendation?
- Which direction is the market moving?
- How confident is the analytical signal?
- Is the underlying system healthy enough to trust the result?

---

# System Architecture

```text
External Market Data
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
        ▼
Persistence Layer
   ┌────┼─────────────┐
   ▼    ▼             ▼
SQLite  JSON State    JSONL Logs
History
   │
   ▼
Historical Analytics
   │
   ▼
Explainability
   │
   ▼
Dashboard / CLI / Notifications
   │
   ▼
Operator
```

Supporting operational subsystems:

```text
Configuration Manager
        │
        ├── Dashboard Override
        ├── Environment Variables
        └── Built-in Defaults

Storage Manager
        │
        ├── Database Initialization
        ├── Schema Versioning
        ├── Schema Migration
        ├── Integrity Validation
        └── Startup Validation

History Manager
        │
        ├── History Recording
        ├── History Retrieval
        ├── Historical Statistics
        ├── Pruning
        └── Retention
```

---

# Development Roadmap

---

# Version 0.1 — Foundation ✅

**Status:** Complete

## Objective

Build a reliable BCH rental decision engine capable of evaluating live rental opportunities and presenting explainable recommendations through an operator dashboard.

## Completed Features

### Core Engine

- Live BCH market data
- BTC market data
- BCH network difficulty
- Network hashrate estimation
- Rental scenario generation
- Budget optimization
- Hashrate optimization
- Strike probability analysis
- Expected revenue calculations
- Expected profit calculations
- ROI calculations
- Risk-adjusted ROI
- Fair Value Ratio
- Pool routing

### Decision Architecture

- Canonical Decision Engine
- Recommendation compatibility layer
- Opportunity Action mapping
- Alert Tier mapping
- Recommendation reasoning
- Waiting-state support

### Market Integrations

- Braiins rental pricing
- MiningRigRentals marketplace
- Multiple pricing-source support

### Intelligence

- Opportunity Score
- Market regime classification
- Explainability engine
- Recommendation History
- Historical comparisons
- Trend Intelligence
- Trend direction
- Trend confidence
- Trend persistence
- Trend velocity
- Trend volatility
- Trend strength
- Interpretation text

### Dashboard

- Streamlit operator dashboard
- Dashboard overview
- Market page
- Market Trends page
- Strike Analysis
- Pool Routing
- Recommendation History
- Historical charts
- Alternative strike plans
- Decision timeline
- Current blockers
- Waiting-state presentation

### Notifications

- Telegram alerts
- Recommendation summaries
- Recommendation-change alerts

### Deployment

- Docker
- Native Umbrel application
- GitHub Container Registry workflow
- Production helper scripts
- Dashboard health checks
- One-command dashboard update workflow

### Persistence

- Current state JSON
- SQLite Recommendation History
- JSONL operational logs
- JSONL log rotation

### Engineering

- Test-Driven Development workflow
- Automated regression suite
- Modular dashboard refactor
- Reusable dashboard utilities
- Dedicated data and service modules

---

# Version 0.2 — Storage & Reliability 🚧

**Status:** Release Hardening

## Objective

Transform the persistence layer into a production-grade storage architecture capable of running safely for long periods while preserving Recommendation History and preventing uncontrolled storage growth.

The Version 0.2 implementation is functionally complete.

Remaining work is focused on:

- Final documentation
- Runtime validation
- Container validation
- Umbrel deployment validation
- Release tagging

---

## Storage Manager ✅

Implementation:

```text
scripts/storage/storage_manager.py
```

Completed:

- [x] Self-initializing database
- [x] Automatic parent-directory creation
- [x] Automatic database creation
- [x] Automatic `run_history` table creation
- [x] Explicit schema versioning
- [x] SQLite `PRAGMA user_version`
- [x] Sequential schema migration runner
- [x] Legacy v0 → v1 migration
- [x] Existing-history preservation during migration
- [x] Unsupported future-schema protection
- [x] Database size reporting
- [x] Database row-count reporting
- [x] SQLite integrity checks
- [x] Storage health model
- [x] SQLite compaction
- [x] Startup storage validation

---

## Schema Management ✅

Completed architecture:

```text
Database Version
        │
        ▼
apply_schema_migrations()
        │
        ▼
Version-Specific Migration
        │
        ▼
CURRENT_SCHEMA_VERSION
```

Current migration:

```text
v0 → v1
```

Completed:

- [x] Current schema version constant
- [x] Legacy database upgrade
- [x] Sequential migration mechanism
- [x] Migration regression tests
- [x] Existing row preservation
- [x] Future-schema rejection
- [x] Idempotent initialization

Future schema changes should extend the sequential migration framework rather than introducing ad hoc database modifications.

---

## Database Integrity ✅

Completed:

- [x] SQLite `PRAGMA integrity_check`
- [x] Storage health reporting
- [x] Startup integrity validation
- [x] Engine startup stops when integrity validation fails
- [x] Database health visible to the dashboard

---

## Startup Validation ✅

The engine now validates storage before normal execution.

Startup flow:

```text
Engine Start
    ↓
Initialize Storage
    ↓
Apply Schema Migrations
    ↓
Run Integrity Check
    ↓
Healthy?
 ┌──┴──┐
 │     │
Yes    No
 │     │
 ▼     ▼
Run   Raise Error
Engine
```

Completed:

- [x] Database initialization before engine execution
- [x] Migration before engine execution
- [x] Integrity validation before engine execution
- [x] Failure stops normal engine processing

---

## History Manager ✅

Implementation:

```text
scripts/storage/history_manager.py
```

Completed:

- [x] Record successful engine executions
- [x] Retrieve recent history
- [x] Retrieve latest values
- [x] Historical trend windows
- [x] History statistics
- [x] Record count
- [x] Oldest timestamp
- [x] Newest timestamp
- [x] Database size
- [x] Oldest-row pruning
- [x] Size-based retention
- [x] Database compaction after pruning

---

## Recommendation History Retention ✅

Version 0.2 introduces managed Recommendation History growth.

### Default Maximum

```text
1 GiB
```

Equivalent to:

```text
1073741824 bytes
```

Configuration:

```text
BCH_HISTORY_MAX_SIZE_BYTES
```

Dashboard override:

```text
history_max_size_bytes
```

Completed:

- [x] Default maximum database size
- [x] User-configurable maximum
- [x] Increase retention limit
- [x] Decrease retention limit
- [x] Unlimited-history mode
- [x] Automatic oldest-row pruning
- [x] Preserve newest history
- [x] Controlled batch deletion
- [x] SQLite VACUUM after pruning
- [x] Safe handling when no rows remain
- [x] Safe handling of impossible byte limits
- [x] Retention regression tests

---

## Unlimited History ✅

A configured maximum of:

```text
0
```

means:

```text
Unlimited
```

Completed:

- [x] Unlimited history supported
- [x] Size-based pruning disabled when unlimited
- [x] Dashboard displays Unlimited
- [x] Configuration system accepts zero
- [x] Operator documentation warns about disk growth

---

## Configuration Manager ✅

Implementation:

```text
scripts/config_manager.py
```

Configuration precedence:

```text
Dashboard Override
        ↓
Environment Variable
        ↓
Built-in Default
```

Completed:

- [x] Centralized configuration loader
- [x] Dashboard override JSON support
- [x] Environment fallback
- [x] Built-in fallback
- [x] Invalid-value safety
- [x] Unlimited-history configuration support
- [x] Dedicated configuration tests

---

## Effective Runtime Configuration ✅

The engine publishes its resolved configuration in:

```text
state/bch_solo_rental_strike_engine.json
```

under:

```text
config
```

Completed:

- [x] Budget configuration published
- [x] Hashrate configuration published
- [x] Duration configuration published
- [x] Mining economics published
- [x] History retention configuration published

This allows the dashboard to display the configuration actually used by the engine.

---

## Dashboard Architecture ✅

The dashboard was modularized during Version 0.2 development to improve maintainability and testing.

Current page modules:

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

Supporting modules include:

```text
dashboard/ui_utils.py
dashboard/decision_utils.py
dashboard/frontier_data.py
dashboard/history_data.py
dashboard/market_utils.py
dashboard/settings_service.py
dashboard/components/
dashboard/charts/
```

Completed:

- [x] Dashboard page extraction
- [x] History page extraction
- [x] Settings page extraction
- [x] Pool Routing page extraction
- [x] Strike Analysis page extraction
- [x] Market Trends page extraction
- [x] Reusable data and service modules
- [x] Reduced `dashboard/app.py` responsibility
- [x] Expanded dashboard unit tests

---

## Storage Dashboard ✅

New page:

```text
Storage
```

Implementation:

```text
dashboard/pages/storage.py
```

Completed:

- [x] Current database size
- [x] Configured maximum size
- [x] Storage utilization
- [x] Record count
- [x] Oldest record
- [x] Newest record
- [x] Database health
- [x] Integrity status
- [x] Unlimited-history display
- [x] Effective runtime configuration display
- [x] Manual Compact Database control

---

## Settings Dashboard ✅

History retention can now be managed through the dashboard Settings page.

Completed:

- [x] Display current retention limit
- [x] Display Unlimited state
- [x] Edit history maximum in GiB
- [x] Convert GiB UI value to canonical bytes
- [x] Save override to JSON
- [x] Request immediate engine run after save

---

## Database Optimization ✅

Completed:

- [x] Manual SQLite VACUUM
- [x] Automatic compaction after pruning
- [x] Dashboard Compact Database button
- [x] Database remains validated after maintenance

---

## Automated Testing ✅

The Version 0.2 development cycle significantly expanded regression coverage.

Current full suite:

```text
251 automated tests
```

New or expanded coverage includes:

- [x] Storage Manager
- [x] History Manager
- [x] Schema versioning
- [x] Schema migration
- [x] Future-schema protection
- [x] Startup storage validation
- [x] History statistics
- [x] History pruning
- [x] Size retention
- [x] Configuration Manager
- [x] Dashboard Settings
- [x] Dashboard utilities
- [x] Decision utilities
- [x] Frontier data
- [x] History data
- [x] Market utilities
- [x] Mocked Yahoo Finance integration boundary

---

## Version 0.2 Release Closeout

The Version 0.2 feature implementation and production validation are complete.

Completed release validation:

- [x] Final README review/update
- [x] Final CHANGELOG review
- [x] Final ROADMAP review
- [x] Final ARCHITECTURE review
- [x] Final CONFIGURATION review
- [x] Final OPERATIONS review
- [x] Final RELEASE_CHECKLIST review
- [x] Compile all production Python modules
- [x] Run full regression suite
- [x] Local runtime validation
- [x] Storage migration runtime validation
- [x] Storage retention/runtime configuration validation
- [x] Dashboard Storage page QA
- [x] Dashboard Settings page QA
- [x] Docker image build and runtime validation
- [x] Umbrel deployment validation
- [x] Production storage verification
- [x] Production history preservation and write verification
- [x] Version updated to v0.2.0
- [x] Release notes prepared
- [ ] Git release tag

---

# Version 0.3 — System Intelligence

**Status:** Next Development Milestone

## Objective

Allow the application to monitor and explain its own operational health.

Version 0.2 establishes the storage-health and startup-validation foundations needed for this milestone.

---

## Planned Features

### Engine Health

- Engine heartbeat
- Last successful execution
- Execution duration
- Consecutive failures
- Last failure timestamp
- Engine status classification

---

### API Health

Monitor external provider availability.

Potential providers:

- BCH market data
- CoinGecko
- Braiins
- MiningRigRentals
- Pool endpoints

Potential metrics:

- Request success
- Request latency
- Last successful response
- Consecutive failures
- Provider status

---

### Pricing Source Status

Provide operator visibility into:

- Active pricing source
- Fallback pricing
- Stale prices
- Unavailable sources
- Provider failures

---

### Rental Source Status

Track:

- Braiins availability
- MiningRigRentals availability
- Listing counts
- Available hashrate
- Pricing health

---

### Database Health

Expand Version 0.2 storage health with:

- Database age
- Last successful write
- Write latency
- Retention activity
- Recent pruning
- Compaction status
- Storage growth rate

---

### Startup Diagnostics

Provide a structured startup report including:

- Configuration validation
- Storage validation
- Provider readiness
- Persistent paths
- Database schema
- Disk availability
- Required files

---

### Automatic Recovery

Potential recovery behavior:

- Retry transient API failures
- Recover stalled background tasks
- Reinitialize safe transient state
- Graceful fallback when providers are unavailable

Automatic recovery should never hide data corruption or destructive storage failures.

---

### Background Task Monitoring

Track:

- Engine execution loop
- Immediate-run trigger
- Scheduled jobs
- Provider polling
- Dashboard availability

---

### Self-Test Framework

Provide a reusable health/self-test subsystem capable of validating:

- Storage
- Providers
- Configuration
- Runtime paths
- External connectivity
- Engine dependencies

---

# Version 0.4 — Forecast Intelligence

**Status:** Planned

## Objective

Move beyond describing current conditions toward estimating future market behavior.

---

## Planned Features

- Trend acceleration
- Trend deceleration
- Trend reversal detection
- Plateau detection
- False-trend detection
- Forecast confidence
- Strike probability forecasting
- Time-to-strike estimation
- Early strike opportunity detection

Forecasting should extend Trend Intelligence rather than replace the Canonical Decision Engine.

---

# Version 0.5 — Historical Intelligence

**Status:** Planned

## Objective

Use accumulated Recommendation History to improve long-term operator insight.

---

## Planned Features

- Historical ROI analysis
- Historical FVR analysis
- Recommendation frequency
- Canonical decision frequency
- Market regime statistics
- Opportunity Score distributions
- Long-term market analytics
- Historical trend comparisons
- Historical storage growth analytics
- Recommendation stability analysis

---

# Version 0.6 — Operator Experience

**Status:** Planned

## Objective

Continue improving usability and overall operator experience.

---

## Planned Features

- First-run setup wizard
- Guided configuration
- Expanded storage management
- Improved dashboard layouts
- Mobile-friendly views
- Dashboard customization
- Export Recommendation History
- Historical playback
- Configuration diagnostics
- Guided health troubleshooting

---

# Version 0.7 — Automation

**Status:** Planned

## Objective

Reduce the need for continuous manual monitoring.

---

## Planned Features

- Scheduled reports
- Telegram improvements
- Discord integration
- Email notifications
- Webhooks
- Daily market summaries
- Automatic diagnostics
- Storage alerts
- Provider-health alerts
- Engine-health alerts

---

# Version 0.8 — Strategy Lab

**Status:** Planned

## Objective

Provide a research environment for evaluating rental strategies against historical conditions.

---

## Planned Features

- Historical replay
- Strategy simulation
- Parameter optimization
- Profitability comparison
- What-if analysis
- Strike replay
- Historical decision replay
- Retention-aware historical datasets

---

# Version 0.9 — Multi-Coin Platform

**Status:** Planned

## Objective

Generalize the analytical framework beyond Bitcoin Cash.

---

## Planned Coins

- Bitcoin
- Litecoin
- Dogecoin
- Kaspa
- Monero
- Additional SHA-256-compatible networks

The multi-coin architecture should reuse:

- Configuration framework
- Storage framework
- Historical framework
- Analytics framework
- Dashboard framework
- Health framework

while keeping coin-specific market and mining assumptions isolated.

---

# Version 1.0 — BCH Rental Intelligence Platform

**Status:** Long-Term Target

## Objective

Deliver a mature production-ready decision-support platform.

---

## Target Characteristics

- Reliable
- Explainable
- Historically aware
- Self-monitoring
- Recoverable
- Extensible
- Production-ready
- Well documented
- Fully tested
- Easy to deploy
- Easy to maintain
- Storage-aware
- Operationally observable

---

# Future Ideas

Potential longer-term additions that are not yet assigned to a specific release.

---

## Analytics

- Machine-learning forecasting
- Market anomaly detection
- Adaptive Opportunity Score
- Multi-factor confidence scoring
- Opportunity clustering
- Market regime forecasting

---

## Dashboard

- Live streaming charts
- Historical playback
- Heat maps
- Opportunity timeline
- Advanced analytics
- System-health overview
- Provider-health dashboard
- Historical storage visualization

---

## Integrations

- Additional rental marketplaces
- Additional exchanges
- Additional mining pool APIs
- Mobile application
- Remote operator interface

---

## Storage

- Maximum-age retention
- Automatic archival before pruning
- Archive management
- Historical export
- Automated backups
- Backup verification
- Cloud synchronization

---

## Operations

- Remote monitoring
- Resource utilization monitoring
- Automatic backup scheduling
- Disaster-recovery automation
- Health notifications
- Deployment telemetry

---

# Guiding Principles

Every feature should improve one or more of the following.

---

## Recommendation Quality

Produce more useful and actionable rental recommendations.

The objective is not necessarily to produce more RENT recommendations.

The objective is to improve the quality and reliability of the decision.

---

## Explainability

Every recommendation should clearly explain why it was generated.

Operators should be able to identify:

- Supporting signals
- Blocking conditions
- Historical context
- Decision thresholds
- Current uncertainty

---

## Reliability

The engine should operate unattended for extended periods without silently corrupting state or losing Recommendation History.

Reliability includes:

- Storage safety
- Configuration safety
- Graceful failures
- Recoverability
- Observable health

---

## Operator Experience

Present complex mining analytics through a simple and intuitive operator workflow.

Operators should not need to inspect source code to understand system state.

---

## Maintainability

Keep the architecture:

- Modular
- Tested
- Documented
- Versioned
- Easy to extend

Avoid duplicating core logic across pages or subsystems.

---

## Performance

Optimize:

- Engine execution
- Storage usage
- Historical retrieval
- Dashboard responsiveness
- Network requests
- Container resource usage

without sacrificing correctness or explainability.

---

## Historical Preservation

Recommendation History is a long-term analytical asset.

Schema changes should migrate historical data rather than destroy it.

Historical data should not be reset as a normal upgrade strategy.

---

## Configuration Transparency

Operators should be able to determine the effective runtime configuration.

Configuration precedence must remain explicit and predictable.

---

## Privacy

Store only information required for engine operation and analytics.

Never collect or store:

- Private keys
- Wallet seed phrases
- Unnecessary personal information
- Sensitive credentials inside Recommendation History

Credentials should remain in protected runtime configuration.

---

# Engineering Workflow

Every feature follows the same development process.

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

Maintaining this workflow is one of the core engineering principles of the BCH Rental Engine.

---

# Release Philosophy

Development should advance through small, verifiable milestones.

Preferred release behavior:

- Small logical commits
- Explicit regression tests
- Backward-compatible migrations
- Clean working trees
- Documented releases
- Tagged production versions
- Verified deployment
- Production validation

A feature is not considered complete merely because the code runs locally.

Completion includes:

```text
Implementation
+
Tests
+
Documentation
+
Runtime Verification
+
Deployment Verification
```

---

# Roadmap Governance

The roadmap should reflect actual implementation status.

A milestone should move to:

```text
Complete
```

only after:

- Feature implementation is complete
- Required automated tests pass
- Documentation is updated
- Runtime validation is complete
- Production deployment is verified where applicable

During release preparation, a milestone may be marked:

```text
Release Hardening
```

when feature development is finished but final release verification remains.

---

# Current Development Status

```text
Version 0.1
Foundation
COMPLETE

        ↓

Version 0.2
Storage & Reliability
PRODUCTION VALIDATED

        ↓

Version 0.3
System Intelligence
NEXT

        ↓

Version 0.4
Forecast Intelligence

        ↓

Version 0.5
Historical Intelligence

        ↓

Version 0.6
Operator Experience

        ↓

Version 0.7
Automation

        ↓

Version 0.8
Strategy Lab

        ↓

Version 0.9
Multi-Coin Platform

        ↓

Version 1.0
BCH Rental Intelligence Platform
```

---

# Long-Term Vision

The BCH Rental Engine has evolved from a simple probability calculator into a modular mining decision-support platform with:

- Live market intelligence
- Scenario optimization
- Canonical decision logic
- Historical evidence
- Trend Intelligence
- Explainability
- Managed persistence
- Operator configuration
- Production deployment
- Operational health foundations

Future development will continue focusing on:

- Better recommendations
- Better explanations
- Better analytics
- Better forecasting
- Better reliability
- Better historical intelligence
- Better operator experience
- Better operational visibility

The long-term objective is to build a platform miners trust—not because it predicts the future perfectly, but because every recommendation is:

- Transparent
- Explainable
- Historically traceable
- Operationally observable
- Reproducible
- Tested
- Backed by measurable evidence

The platform should become more capable without becoming less understandable.