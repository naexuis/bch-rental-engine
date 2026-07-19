# Changelog

All notable changes to the BCH Rental Engine are documented in this file.

The project follows the principles of **Keep a Changelog** and **Semantic Versioning (SemVer)**.

---

# [Unreleased]

## Added

- Deployment & Operations (v2.1) development.

## Planned

### v2.1 — Deployment & Operations

- One-command dashboard deployment
- One-command dashboard update
- One-command dashboard restart
- Dashboard health checks
- Automatic Docker rebuild
- Deployment verification
- Version information within the dashboard
- Build metadata display

---

# [v2.0.1] - 2026-07-19

## Overview

Version 2.0.1 is the first patch release following the Dashboard V2 launch.

This release focused on final dashboard polish, recommendation messaging improvements, version tagging, and production deployment.

---

## Changed

### Dashboard

- Refined dashboard labels for improved readability.
- Improved recommendation messaging.
- Increased consistency across recommendation terminology.
- Final UI polish for the Dashboard V2 Operator Console.

---

## Operational

- Tagged production release as **v2.0.1**.
- Updated GitHub release history.
- Production deployment to Umbrel completed.

---

## Fixed

- Minor dashboard wording inconsistencies.

---

# [v2.0.0] - 2026-07-19

## Overview

Version 2.0.0 represents the completion of Dashboard V2 and marks the project's transition from a prototype into a polished operational decision platform.

The dashboard was completely redesigned around an operator-first workflow.

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
- Expandable advanced analysis sections

---

### User Experience

- Operator-first dashboard workflow
- Improved recommendation hierarchy
- Clear separation between recommendation and market state
- Improved execution plan messaging

---

### Development

- Dashboard V2 design document
- Dashboard wireframe
- Feature branch workflow
- Improved Git workflow
- Semantic version tagging

---

### Deployment

- Docker deployment improvements
- Umbrel production deployment
- Production release tagging

---

## Changed

- Complete dashboard redesign.
- Improved recommendation workflow.
- Reorganized dashboard layout.
- Simplified navigation.
- Reduced dashboard complexity.
- Improved readability.
- Improved recommendation consistency.

---

## Fixed

- Recommendation banner behavior.
- Dashboard layout inconsistencies.
- Opportunity score presentation.
- Recommendation mapping.
- Multiple UI polish issues.

---

# [v1.1.0] - 2026-07

## Overview

Version 1.1.0 focused on improving visualization, documentation, deployment, and operational reliability.

### Added

#### Dashboard

- Historical Performance page
- Interactive BCH candlestick charts
- Multiple market time ranges
- Market overview improvements
- Pool routing visualization

#### Engine

- Opportunity scoring
- Market regime classification
- Historical SQLite database
- Recommendation history recording

#### Operational

- Automatic JSONL log rotation
- Configurable logging
- SQLite history storage

#### Deployment

- Docker deployment
- Umbrel deployment
- AWS EC2 deployment documentation

#### Documentation

- README
- Installation Guide
- Configuration Guide
- Architecture Guide
- Operations Runbook
- Developer Journal
- Roadmap

---

## Changed

- Dashboard layout improvements.
- Documentation organization.
- Repository structure.

---

## Fixed

- Dashboard rendering.
- Pool routing display.
- JSON parsing.
- Long-term log growth.

---

# [v1.0.0] - 2026-07

## Overview

Initial production-ready release.

### Added

#### Core Engine

- BCH market data collection
- Difficulty tracking
- Network hashrate estimation
- Braiins integration
- MiningRigRentals integration
- Strike optimization
- Poisson probability engine
- Expected revenue/profit calculations
- ROI calculations
- Risk-adjusted ROI
- Fair Value Ratio (FVR)
- Recommendation engine

#### Dashboard

- Initial Streamlit dashboard
- Market overview
- Strike analysis
- Pool routing

#### Storage

- JSON state output
- SQLite history
- JSONL operational logs

#### Notifications

- Telegram alerts

#### Deployment

- Docker deployment
- Umbrel deployment

---

# Version History

| Version | Status | Description |
|----------|--------|-------------|
| v2.0.1 | Current | Dashboard V2 polish and production release |
| v2.0.0 | Stable | Dashboard V2 Operator Console |
| v1.1.0 | Stable | Dashboard enhancements and documentation |
| v1.0.0 | Stable | Initial production release |

---

# Roadmap

## v2.1 — Deployment & Operations

- One-command deployment
- Deployment automation
- Health monitoring
- Version display
- Build metadata

---

## v2.2 — Recommendation History

- Recommendation timeline
- Historical analytics
- Recommendation stability
- Export functionality

---

## v2.3 — Notifications

- Telegram alerts
- Recommendation change alerts
- Threshold notifications
- Daily and weekly summaries

---

## v2.4 — Scenario Simulator

- BCH price sensitivity
- Rental price sensitivity
- Difficulty sensitivity
- ROI simulation
- Interactive "What If?" analysis

---

## v2.5 — Recommendation Explainability

- Decision factor contributions
- Confidence explanation
- Recommendation comparison
- Threshold analysis

---

## v3.0 — Multi-Coin Rental Platform

- Shared engine framework
- Pluggable coin architecture
- BCH support
- BTC support
- DGB support
- Cross-coin comparison dashboard

---

## v4.0 — Umbrel Community App

- Native Umbrel application
- One-click installation
- Configuration wizard
- Automatic updates
- Comprehensive documentation
- Community release

---

# Release Philosophy

The BCH Rental Engine follows a conservative release strategy.

- **Major versions** introduce significant architectural or platform changes.
- **Minor versions** introduce new capabilities while maintaining compatibility.
- **Patch versions** focus on stability, usability, bug fixes, and documentation.

Each release strives to improve one or more of the following:

- Explainability
- Reliability
- Performance
- Maintainability
- User Experience
- Operational Excellence