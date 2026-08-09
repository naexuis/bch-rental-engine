# Changelog

All notable changes to the BCH Rental Engine are documented in this file.

The project follows the principles of **Keep a Changelog** and **Semantic Versioning (SemVer)**.

---

# Current Release Line

The current BCH Rental Engine release line uses the native Umbrel application roadmap:

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

Earlier `v1.x` and `v2.x` releases documented later in this file represent the project's legacy development and deployment history before the current native Umbrel release line was established.

---

# [Unreleased]

## Overview

Development is currently focused on completing **Version 0.2 — Storage & Reliability**.

Version 0.2 transforms the persistence subsystem from basic SQLite history storage into a managed, validated, versioned, and operator-visible storage architecture suitable for long-term production operation.

Feature development for the Version 0.2 milestone is substantially complete.

Current work is focused on:

- Release hardening
- Documentation
- Runtime validation
- Docker validation
- Umbrel production validation
- Final release tagging

---

## Added

### Storage Manager

Added a dedicated storage-management subsystem:

```text
scripts/storage/storage_manager.py
```

Capabilities include:

- Automatic database directory creation
- Automatic SQLite database creation
- Automatic `run_history` table initialization
- Explicit database schema versioning
- SQLite `PRAGMA user_version` support
- Sequential schema migrations
- Database integrity checks
- Database size reporting
- History row-count reporting
- Storage health reporting
- SQLite compaction
- Startup storage validation

---

### Schema Versioning

Added explicit SQLite schema version management.

The storage subsystem now maintains a canonical schema version and records it through:

```sql
PRAGMA user_version;
```

This provides a controlled mechanism for evolving Recommendation History without requiring destructive database recreation.

---

### Schema Migration Framework

Added sequential schema migrations.

Current migration path:

```text
v0 → v1
```

The migration framework:

- Detects the current database schema version
- Applies required migrations sequentially
- Preserves existing Recommendation History
- Updates the stored schema version
- Rejects unsupported future schema versions
- Supports idempotent initialization

Future schema changes should extend this migration framework instead of introducing ad hoc database modifications.

---

### Startup Storage Validation

Added storage validation during engine startup.

The engine now performs:

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
Run   Stop
Engine
```

If SQLite integrity validation fails, normal engine execution is stopped rather than continuing with an unhealthy history database.

---

### Database Integrity Checks

Added SQLite integrity validation using:

```sql
PRAGMA integrity_check;
```

Storage health now reports whether the Recommendation History database passes integrity validation.

---

### Storage Health Model

Added structured storage-health reporting.

Current storage-health information includes:

- Database existence
- Database size
- History row count
- Integrity status

Storage health is included in the engine's current-state output and is available to the dashboard.

---

### History Manager

Expanded the Recommendation History subsystem with production-oriented history-management capabilities.

Capabilities include:

- Recording successful engine executions
- Retrieving historical observations
- Retrieving latest values
- Historical trend windows
- History statistics
- Record count
- Oldest record timestamp
- Newest record timestamp
- Database size reporting
- Oldest-row pruning
- Size-based retention
- Database optimization after pruning

---

### Recommendation History Retention

Added automatic Recommendation History retention management.

Default maximum history database size:

```text
1 GiB
```

Equivalent to:

```text
1073741824 bytes
```

The retention manager removes the oldest Recommendation History records when the configured maximum size is exceeded.

The newest history is preserved.

---

### Unlimited History Mode

Added support for unlimited Recommendation History retention.

A configured maximum of:

```text
0
```

means:

```text
Unlimited
```

When unlimited history is enabled:

- Automatic size-based pruning is disabled
- Recommendation History may grow without an application-enforced maximum
- The dashboard displays the retention mode as Unlimited

Operators using this mode are responsible for monitoring available disk capacity.

---

### Database Compaction

Added SQLite compaction using:

```sql
VACUUM;
```

Compaction can occur:

- Automatically after history pruning
- Manually through the Storage dashboard

This allows SQLite to return unused pages to the filesystem after historical records are deleted.

---

### Configuration Manager

Added centralized runtime configuration handling:

```text
scripts/config_manager.py
```

Configuration precedence is now:

```text
Dashboard Override
        ↓
Environment Variable
        ↓
Built-in Default
```

This provides one predictable configuration-resolution mechanism for settings that support dashboard overrides.

---

### History Retention Configuration

Added:

```text
BCH_HISTORY_MAX_SIZE_BYTES
```

Default:

```text
1073741824
```

The same setting can be overridden through:

```text
config/dashboard_config_override.json
```

using:

```json
{
  "history_max_size_bytes": 1073741824
}
```

A value of:

```text
0
```

disables automatic size-based pruning.

---

### Effective Runtime Configuration

Expanded the current engine state to expose resolved runtime configuration.

The current-state JSON now publishes configuration under:

```text
config
```

including:

- Budget minimum
- Budget maximum
- Budget step
- Minimum duration
- Maximum duration
- Pool fee
- Orphan/stale risk
- Slippage
- Price movement buffer
- Hashrate minimum
- Hashrate maximum
- Hashrate step
- History maximum size

This allows the dashboard to display the configuration actually used by the most recent engine execution.

---

### Settings Service

Added dashboard configuration service functionality for:

- Loading configuration overrides
- Resolving effective setting values
- Saving configuration overrides
- Requesting an immediate engine execution after configuration changes

---

### History Retention Settings

Expanded the dashboard Settings page to manage Recommendation History retention.

Operators can now:

- View the current retention limit
- View Unlimited retention state
- Configure maximum history size in GiB
- Disable the application-enforced history limit
- Save the setting to the dashboard override file
- Request an immediate engine run after saving

The dashboard converts the operator-facing GiB value into canonical bytes before saving the override.

---

### Storage Dashboard

Added a dedicated:

```text
Storage
```

dashboard page.

Implementation:

```text
dashboard/pages/storage.py
```

The page provides visibility into:

- Current database size
- Configured maximum size
- Storage utilization
- Recommendation History row count
- Oldest record
- Newest record
- Database health
- Integrity status
- Effective retention configuration
- Unlimited-history mode

The page also provides a manual:

```text
Compact Database
```

control.

---

### Modular Dashboard Architecture

Continued the dashboard modularization effort.

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

This reduces the responsibility of:

```text
dashboard/app.py
```

and separates presentation, data access, configuration, charting, and decision utilities.

---

### Immediate Engine Run Trigger

Added support for requesting an immediate engine execution from dashboard configuration changes.

The engine launcher watches:

```text
config/run_now.trigger
```

and can execute the engine without waiting for the next normal scheduled cycle.

---

### Storage Tests

Added and expanded automated tests covering:

- Database initialization
- Database directory creation
- Schema versioning
- Schema migration
- Existing-history preservation
- Future-schema rejection
- Database integrity
- Storage health
- Startup validation
- Failed-integrity startup rejection
- History statistics
- History pruning
- Size-based retention
- Unlimited retention
- SQLite compaction

---

### Configuration Tests

Added automated tests covering:

- Dashboard override precedence
- Environment-variable fallback
- Built-in defaults
- Invalid configuration handling
- History retention configuration
- Unlimited-history configuration

---

### Dashboard Tests

Expanded dashboard unit testing around modularized functionality including:

- Decision utilities
- Dashboard UI utilities
- Frontier data
- History data
- Market utilities
- Settings behavior
- External market-data boundaries

---

## Changed

### Engine Startup

Engine startup now validates persistent storage before normal market and scenario processing begins.

This moves storage validation from a passive diagnostic capability into an operational safety mechanism.

---

### Engine State

The current-state JSON now contains additional operational information, including:

- Effective runtime configuration
- Storage health
- History retention configuration

This makes the state file a more complete representation of the engine execution environment.

---

### Recommendation History

Recommendation History is now treated as a managed long-term analytical asset rather than an indefinitely growing SQLite file.

History growth is controlled by a configurable retention policy while preserving recent observations.

---

### Configuration Architecture

Selected runtime settings can now be controlled through dashboard overrides while retaining environment-variable compatibility.

The configuration system uses explicit precedence instead of duplicating configuration logic across the engine and dashboard.

---

### Dashboard Navigation

Dashboard navigation now includes dedicated:

```text
Storage
```

and:

```text
Settings
```

operational pages.

This separates system administration from analytical pages such as Market, Market Trends, Strike Analysis, and Recommendation History.

---

### Dashboard Structure

Large sections of dashboard logic have been extracted from the main Streamlit application into dedicated modules.

The main application increasingly acts as:

- Application bootstrap
- State loader
- Navigation router
- Page coordinator

rather than containing all presentation and business logic directly.

---

### Testing

The automated regression suite has expanded to:

```text
251 tests
```

with the full suite currently passing during Version 0.2 release hardening.

---

## Reliability

Version 0.2 substantially improves the engine's ability to operate unattended.

Reliability improvements include:

- Automatic storage initialization
- Schema migration
- Database integrity checking
- Startup validation
- Controlled Recommendation History growth
- Database compaction
- Effective configuration reporting
- Storage-health visibility
- Increased automated regression coverage

---

## Documentation

Updated documentation for the Version 0.2 architecture and release process, including:

- `CONFIGURATION.md`
- `OPERATIONS.md`
- `ARCHITECTURE.md`
- `ROADMAP.md`
- `RELEASE_CHECKLIST.md`
- `CHANGELOG.md`

Documentation now reflects:

- Storage Manager architecture
- History Manager architecture
- Schema versioning
- Schema migration
- Storage retention
- Unlimited-history mode
- Configuration precedence
- Storage dashboard
- Settings dashboard
- Startup validation
- Version 0.2 release-hardening workflow

---

## Remaining Before v0.2.0

The Version 0.2 feature implementation is substantially complete.

Remaining release tasks include:

- [ ] Final README review
- [ ] Final documentation consistency review
- [ ] Compile all production Python modules
- [ ] Run final full regression suite
- [ ] Local runtime validation
- [ ] Database migration runtime validation
- [ ] Retention runtime validation
- [ ] Dashboard Storage page QA
- [ ] Dashboard Settings page QA
- [ ] Docker engine build validation
- [ ] Docker dashboard build validation
- [ ] Umbrel deployment validation
- [ ] Production storage-health verification
- [ ] Production Recommendation History verification
- [ ] Final version update
- [ ] Release notes
- [ ] Git release tag

---

# [v0.1.x] — Foundation

## Overview

Version 0.1 established the current BCH Rental Engine application architecture.

The milestone created the foundation for the engine, analytical framework, operator dashboard, native Umbrel deployment, Recommendation History, Trend Intelligence, and explainable decision model.

---

## Added

### Core Engine

- Live BCH market data
- BTC market data
- BCH network difficulty
- Network hashrate estimation
- Rental scenario generation
- Budget optimization
- Hashrate optimization
- Pool routing
- Poisson block-probability analysis
- Expected revenue
- Expected profit
- ROI
- Risk-adjusted ROI
- Fair Value Ratio

---

### Decision Architecture

- Canonical Decision Engine
- Canonical operator decisions
- Recommendation compatibility mapping
- Opportunity Action mapping
- Alert Tier mapping
- Recommendation reasoning
- Waiting-state support

Canonical decisions include:

```text
RENT_NOW
READY
WATCH_CLOSELY
WATCH
WAIT
UNAVAILABLE
```

---

### Opportunity Intelligence

- Opportunity Score
- Market regime classification
- Recommendation explanations
- Current blockers
- Conditions required for stronger recommendations

---

### Recommendation History

- SQLite historical database
- Historical recommendation recording
- Historical metric retrieval
- Recommendation change tracking
- Opportunity Score history

---

### Trend Intelligence

- Trend direction
- Trend confidence
- Trend persistence
- Trend velocity
- Trend volatility
- Trend strength
- High-velocity trend promotion
- Interpretation integration

---

### Market Integrations

- Braiins
- MiningRigRentals
- Multiple rental-pricing sources

---

### Dashboard

- Streamlit operator dashboard
- Dashboard overview
- Market page
- Market Trends
- Strike Analysis
- Pool Routing
- Recommendation History
- Historical charts
- Recommended strike
- Recommended pool
- Alternative strike plans
- Current blockers
- Decision timeline
- Waiting-state presentation

---

### Notifications

- Telegram alerts
- Recommendation summaries
- Recommendation-change notifications

---

### Persistence

- Current-state JSON
- SQLite Recommendation History
- JSONL operational logging
- Automatic JSONL rotation

---

### Deployment

- Docker support
- Native Umbrel application
- GitHub Container Registry workflow
- Production helper scripts
- Dashboard health checks
- One-command dashboard update workflow

---

### Engineering

- Test-Driven Development workflow
- Automated regression testing
- Modular architecture
- Documentation framework
- Release workflow

---

# Legacy Development History

The releases below predate the current native Umbrel `v0.x` roadmap.

They are retained because they document important stages in the project's development.

They should not be interpreted as the current application release sequence.

---

# [v2.1.0] - 2026-07-19

## Overview

Version 2.1.0 introduced the BCH Rental Engine Operations Toolkit.

This release replaced much of the manual Docker dashboard deployment process with reusable operational scripts for building, deploying, restarting, updating, checking, and versioning the dashboard.

---

## Added

### Operations Toolkit

- Shared shell utilities in `scripts/common.sh`
- Centralized deployment configuration in `scripts/config.sh`
- Environment-aware Docker detection in `scripts/docker_helper.sh`
- Dashboard image build automation
- Dashboard deployment automation
- Dashboard restart automation
- One-command dashboard update workflow
- Dashboard health checks
- Git version and release reporting

---

### Deployment

- Automatic Docker image verification
- Automatic existing-container replacement
- Dashboard availability polling after deployment
- Post-deployment health verification
- Support for environments requiring `sudo docker`
- Automatic Git tag retrieval during updates

---

## Changed

The preferred Umbrel dashboard update workflow became:

```bash
cd ~/bch_rental_engine
./scripts/update_dashboard.sh
```

---

# [v2.0.1] - 2026-07-19

## Overview

Version 2.0.1 was the first patch release following the Dashboard V2 launch.

The release focused on dashboard polish, recommendation messaging improvements, version tagging, and production deployment.

---

## Changed

### Dashboard

- Refined dashboard labels
- Improved recommendation messaging
- Increased consistency across recommendation terminology
- Final UI polish for the Dashboard V2 Operator Console

---

## Operational

- Tagged production release as `v2.0.1`
- Updated GitHub release history
- Completed production deployment to Umbrel

---

## Fixed

- Minor dashboard wording inconsistencies

---

# [v2.0.0] - 2026-07-19

## Overview

Version 2.0.0 represented the completion of Dashboard V2 and the project's transition from an early prototype toward an operator-focused decision platform.

The dashboard was redesigned around an operator-first workflow.

---

## Added

### Dashboard

- Decision Center
- Operator Action banner
- Decision Drivers
- Recommended Strike
- Recommended Pool
- Alternative Strike Plans
- Current Blockers
- Conditions Needed for RENT
- Confidence scoring
- Improved recommendation explanations
- Simplified navigation
- Expandable advanced-analysis sections

---

### User Experience

- Operator-first dashboard workflow
- Improved recommendation hierarchy
- Clearer separation between recommendation and market state
- Improved execution-plan messaging

---

### Development

- Dashboard V2 design document
- Dashboard wireframe
- Feature-branch workflow
- Improved Git workflow
- Semantic version tagging

---

### Deployment

- Docker deployment improvements
- Umbrel production deployment
- Production release tagging

---

## Changed

- Complete dashboard redesign
- Improved recommendation workflow
- Reorganized dashboard layout
- Simplified navigation
- Reduced dashboard complexity
- Improved readability
- Improved recommendation consistency

---

## Fixed

- Recommendation banner behavior
- Dashboard layout inconsistencies
- Opportunity Score presentation
- Recommendation mapping
- Multiple UI polish issues

---

# [v1.1.0] - 2026-07

## Overview

Version 1.1.0 focused on visualization, documentation, deployment, historical persistence, and operational reliability.

---

## Added

### Dashboard

- Historical Performance page
- Interactive BCH candlestick charts
- Multiple market time ranges
- Market overview improvements
- Pool-routing visualization

---

### Engine

- Opportunity scoring
- Market regime classification
- Historical SQLite database
- Recommendation History recording

---

### Operations

- Automatic JSONL log rotation
- Configurable logging
- SQLite historical storage

---

### Deployment

- Docker deployment
- Umbrel deployment
- AWS EC2 deployment documentation

---

### Documentation

- README
- Installation Guide
- Configuration Guide
- Architecture Guide
- Operations Runbook
- Developer Journal
- Roadmap

---

## Changed

- Dashboard layout
- Documentation organization
- Repository structure

---

## Fixed

- Dashboard rendering
- Pool-routing display
- JSON parsing
- Long-term log growth

---

# [v1.0.0] - 2026-07

## Overview

Initial production-oriented release of the BCH Rental Engine.

---

## Added

### Core Engine

- BCH market-data collection
- Difficulty tracking
- Network hashrate estimation
- Braiins integration
- MiningRigRentals integration
- Strike optimization
- Poisson probability engine
- Expected revenue calculations
- Expected profit calculations
- ROI calculations
- Risk-adjusted ROI
- Fair Value Ratio
- Recommendation engine

---

### Dashboard

- Initial Streamlit dashboard
- Market overview
- Strike analysis
- Pool routing

---

### Storage

- JSON state output
- SQLite history
- JSONL operational logs

---

### Notifications

- Telegram alerts

---

### Deployment

- Docker deployment
- Umbrel deployment

---

# Version History

## Current Release Line

| Version | Status | Description |
|---------|--------|-------------|
| v0.2.x | Release Hardening | Storage & Reliability |
| v0.1.x | Complete | Foundation |

## Planned Release Line

| Version | Status | Description |
|---------|--------|-------------|
| v0.3 | Next | System Intelligence |
| v0.4 | Planned | Forecast Intelligence |
| v0.5 | Planned | Historical Intelligence |
| v0.6 | Planned | Operator Experience |
| v0.7 | Planned | Automation |
| v0.8 | Planned | Strategy Lab |
| v0.9 | Planned | Multi-Coin Platform |
| v1.0 | Long-Term Target | BCH Rental Intelligence Platform |

## Legacy Development Releases

| Version | Status | Description |
|---------|--------|-------------|
| v2.1.0 | Legacy | Deployment & Operations Toolkit |
| v2.0.1 | Legacy | Dashboard V2 polish |
| v2.0.0 | Legacy | Dashboard V2 Operator Console |
| v1.1.0 | Legacy | Dashboard, history, and operational enhancements |
| v1.0.0 | Legacy | Initial production-oriented release |

---

# Upcoming Milestones

## v0.2 — Storage & Reliability

Current status:

```text
RELEASE HARDENING
```

Primary capabilities:

- Storage Manager
- History Manager
- Schema versioning
- Schema migrations
- Database integrity validation
- Startup validation
- Recommendation History retention
- Storage statistics
- Database optimization
- Storage dashboard
- Retention configuration

---

## v0.3 — System Intelligence

Planned capabilities:

- Engine Health
- API Health
- Pricing Source Status
- Rental Source Status
- Expanded Database Health
- Startup Diagnostics
- Automatic Recovery
- Background Task Monitoring
- Self-Test Framework

---

## v0.4 — Forecast Intelligence

Planned capabilities:

- Trend acceleration
- Trend deceleration
- Trend reversal detection
- Plateau detection
- False-trend detection
- Forecast confidence
- Strike probability forecasting
- Time-to-strike estimation
- Early strike opportunity detection

---

## v0.5 — Historical Intelligence

Planned capabilities:

- Historical ROI analysis
- Historical FVR analysis
- Recommendation frequency
- Canonical decision frequency
- Market regime statistics
- Opportunity Score distributions
- Long-term market analytics
- Historical trend comparison
- Recommendation stability analysis

---

## v0.6 — Operator Experience

Planned capabilities:

- First-run setup wizard
- Guided configuration
- Expanded storage management
- Improved dashboard layouts
- Mobile-friendly views
- Dashboard customization
- Export Recommendation History
- Historical playback

---

## v0.7 — Automation

Planned capabilities:

- Scheduled reports
- Telegram improvements
- Discord integration
- Email notifications
- Webhooks
- Daily market summaries
- Automatic diagnostics
- System-health alerts

---

## v0.8 — Strategy Lab

Planned capabilities:

- Historical replay
- Strategy simulation
- Parameter optimization
- Profitability comparison
- What-if analysis
- Strike replay

---

## v0.9 — Multi-Coin Platform

Planned expansion beyond BCH.

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

A mature, explainable, historically aware, self-monitoring, extensively tested, and production-ready rental intelligence platform.

---

# Release Philosophy

The BCH Rental Engine follows a conservative release strategy.

## Major Versions

Major versions represent significant architectural or platform milestones.

## Minor Versions

Minor versions introduce new capabilities while maintaining compatibility wherever practical.

## Patch Versions

Patch versions focus on:

- Stability
- Reliability
- Usability
- Bug fixes
- Documentation
- Operational improvements

---

# Release Requirements

A feature is not considered complete merely because the implementation works locally.

Completion requires:

```text
Implementation
+
Automated Tests
+
Compilation
+
Documentation
+
Runtime Validation
+
Regression Testing
+
Deployment Verification
```

A release should not be tagged until its applicable release checklist has been completed.

---

# Engineering Principles

Every release should improve one or more of the following:

- Recommendation Quality
- Explainability
- Reliability
- Historical Intelligence
- Performance
- Maintainability
- Operator Experience
- Operational Excellence

The platform should become more capable without becoming less understandable.