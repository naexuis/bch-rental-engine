# Changelog

All notable changes to the BCH Solo Rental Strike Engine are documented in this file.

The format is based on **Keep a Changelog**, and the project follows **Semantic Versioning** where practical.

---

# [Unreleased]

## Added

- Placeholder for future features.

## Changed

- Placeholder for future improvements.

## Fixed

- Placeholder for future bug fixes.

---

# [v1.1.0] - 2026-07

## Overview

Version 1.1.0 represents the first fully documented release of the BCH Solo Rental Strike Engine.

This release focused on improving usability, visualization, deployment, operational reliability, and long-term maintainability.

---

## Added

### Dashboard

- Decision Center redesign
- Historical Performance page
- Interactive BCH candlestick charts
- Multiple market time ranges
    - 24 Hours
    - 3 Days
    - 7 Days
    - 30 Days
    - 1 Year
- Improved market overview
- Pool routing visualization
- Human-readable market metrics
- Opportunity score display
- Market regime display

---

### Engine

- Pool routing recommendation engine
- Opportunity scoring
- Market regime classification
- Historical SQLite database
- Historical recommendation recording
- Improved recommendation summaries

---

### Operational

- Automatic JSONL log rotation
- Configurable log size limits
- Configurable log backup count
- Improved operational logging
- SQLite history storage

---

### Deployment

- Docker dashboard deployment
- Umbrel deployment support
- AWS EC2 deployment documentation
- Portable Linux deployment support

---

### Documentation

Added comprehensive project documentation including:

- README
- Installation Guide
- Configuration Guide
- Architecture Guide
- Operations Runbook
- EC2 Deployment Guide
- Decision Log
- Developer Journal
- Project Roadmap

---

## Changed

- Dashboard layout redesigned.
- Decision workflow simplified.
- Market metrics displayed using readable units.
- Documentation structure standardized.
- Repository organization improved.

---

## Fixed

- Pool routing display issues.
- Dashboard rendering improvements.
- Historical dashboard loading issues.
- Improved JSON parsing.
- Improved operational stability.
- Reduced long-term log growth through automatic rotation.

---

## Performance

- Reduced dashboard complexity.
- Improved dashboard responsiveness.
- Improved operational reliability.
- Improved long-term maintainability.

---

# [v1.0.0] - 2026-07

## Overview

Version 1.0.0 represents the first production-ready release of the BCH Solo Rental Strike Engine.

The core optimization engine was completed along with the initial dashboard and deployment architecture.

---

## Added

### Core Engine

- BCH market data collection
- BCH difficulty tracking
- Network hashrate estimation
- Braiins hashpower support
- MiningRigRentals support
- Budget optimization
- Hashrate optimization
- Strike evaluation engine
- Poisson probability modeling
- Expected revenue calculations
- Expected profit calculations
- ROI calculations
- Risk-adjusted ROI
- Fair Value Ratio (FVR)
- Strike grading
- Recommendation engine

---

### Dashboard

- Initial Streamlit dashboard
- Market overview
- Strike analysis
- Pool routing
- Historical visualization

---

### Data Storage

- JSON state output
- SQLite historical database
- JSONL operational logs

---

### Notifications

- Telegram alert support

---

### Deployment

- Docker dashboard
- Umbrel deployment

---

## Initial Architecture

The project architecture was established around four primary components:

- Optimization Engine
- JSON State Output
- SQLite History
- Streamlit Dashboard

---

# Version History

| Version | Status | Description |
|----------|--------|-------------|
| v1.1.0 | Current | Dashboard enhancements, documentation, candlestick charts, log rotation |
| v1.0.0 | Stable | Initial production release |

---

# Upgrade Notes

## Upgrading from v1.0.0 to v1.1.0

Recommended steps:

1. Pull the latest repository.
2. Rebuild the Docker dashboard image.
3. Restart the dashboard container.
4. Review the updated documentation.
5. Verify the SQLite history database.
6. Verify candlestick charts are loading correctly.
7. Verify automatic log rotation is functioning.

No database migration is required.

Existing SQLite history files remain fully compatible.

---

# Future Releases

The following features are currently planned for future releases.

## v1.2.x

- Technical Analysis Engine
- RSI
- MACD
- Bollinger Bands
- Moving Averages
- Dashboard indicator overlays

---

## v1.3.x

- Historical strategy backtesting
- Performance analytics
- Historical recommendation explorer

---

## v1.4.x

- Dashboard settings editor
- Automated scheduling improvements
- Additional notification channels

---

## v2.0

- AI-assisted decision support
- Multi-coin architecture
- REST API
- Advanced forecasting
- Machine learning enhancements
- Automated rental execution

---

# Release Philosophy

The project follows a conservative release strategy.

- Major versions introduce significant architectural changes.
- Minor versions add substantial new functionality while maintaining compatibility.
- Patch versions focus on bug fixes, stability improvements, and documentation updates.

Every release aims to improve one or more of the following:

- Explainability
- Reliability
- Performance
- Maintainability
- Portability
- User experience