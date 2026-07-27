# BCH Rental Engine Roadmap

The BCH Rental Engine is an open-source decision-support platform for evaluating Bitcoin Cash (BCH) hashpower rental opportunities.

Rather than attempting to predict the future with a black-box algorithm, the engine provides transparent, explainable, and data-driven recommendations that help operators answer one simple question:

> **"Should I rent hashpower right now?"**

The long-term vision is to build the most comprehensive and trusted analytics platform for cryptocurrency hashpower rentals.

---

# Current Version

**Version:** v0.1.x

**Status:** Active Development

**Platform:** Native Umbrel Application

---

# Project Vision

The BCH Rental Engine combines:

- Live market pricing
- Network conditions
- Rental marketplace pricing
- Statistical probability
- Risk-adjusted profitability
- Historical analytics
- Trend intelligence
- Explainable decision logic
- Operational monitoring
- System health management

The objective is not to automate mining decisions.

The objective is to explain them.

Every recommendation should clearly answer:

- Should I rent?
- Why?
- What changed?
- What is preventing a better recommendation?
- Which direction is the market moving?
- How confident is the recommendation?

---

# System Architecture

```
Market Data
      │
      ▼
Opportunity Analysis
      │
      ▼
Recommendation Engine
      │
      ▼
Persistence Layer
      │
      ├───────────────┐
      ▼               ▼
Current State     Historical Data
(JSON)              (SQLite)
      │               │
      └──────┬────────┘
             ▼
      Analytics Layer
             │
             ▼
      Dashboard / API
             │
             ▼
          Operator
```

---

# Development Roadmap

---

# Version 0.1 — Foundation ✅

Status

Complete

## Objectives

Build a reliable decision engine capable of evaluating BCH rental opportunities and presenting recommendations through a modern dashboard.

## Completed Features

### Core Engine

- Live BCH market data
- BCH network difficulty
- Network hashrate estimation
- Opportunity scoring
- Recommendation engine
- Budget optimization
- Hashrate optimization
- Pool routing

### Market Integrations

- Braiins marketplace
- MiningRigRentals marketplace
- Multiple pricing source support

### Intelligence

- Opportunity Score
- Explainability engine
- Trend Intelligence
- Historical comparisons
- Recommendation reasoning

### Dashboard

- Streamlit operator dashboard
- Strike Analysis
- Market Overview
- Pool Routing
- Historical charts
- Waiting-state support

### Notifications

- Telegram alerts
- Recommendation summaries

### Deployment

- Docker
- Native Umbrel App
- GitHub Container Registry
- Automatic updates

### Persistence

- Current state JSON
- SQLite history
- JSONL logging

---

# Version 0.2 — Storage & Reliability 🚧

Current Development Focus

The goal of this release is to transform the storage subsystem into a production-grade architecture suitable for long-term operation.

## Storage Manager

- Self-initializing database
- Automatic database creation
- Schema migrations
- Database integrity checks
- Startup validation

## History Manager

- Record every engine execution
- Summarized execution history
- Automatic history pruning
- Storage statistics
- Database optimization

## Storage Management

### Retention Modes

- Unlimited history
- Maximum database size (default)
- Future support for maximum age

### Default Configuration

Maximum History Size

```
1 GB
```

Users may increase, decrease, or disable storage limits.

## Dashboard

Storage page including:

- Current database size
- Configured maximum size
- Record count
- Oldest record
- Newest record
- Database health
- Manual Compact Database button

## Future

Optional archive support before pruning.

---

# Version 0.3 — System Intelligence

Objective

Allow the application to monitor its own operational health.

## Planned Features

- Engine Health
- API Health
- Pricing Source Status
- Rental Source Status
- Database Health
- Startup Diagnostics
- Automatic Recovery
- Background Task Monitoring
- Self-test Framework

---

# Version 0.4 — Forecast Intelligence

Objective

Move beyond describing current conditions toward estimating future market behavior.

## Planned Features

- Trend acceleration
- Trend deceleration
- Trend reversal detection
- Plateau detection
- Forecast confidence
- Strike probability forecasting
- Time-to-strike estimation

---

# Version 0.5 — Historical Intelligence

Objective

Use historical execution data to improve operator insight.

## Planned Features

- Historical ROI analysis
- Historical FVR analysis
- Recommendation frequency
- Market regime statistics
- Historical Opportunity Score distributions
- Long-term market analytics
- Trend comparisons

---

# Version 0.6 — Operator Experience

Objective

Continue improving usability and overall user experience.

## Planned Features

- First-run setup wizard
- Guided configuration
- Storage management interface
- Improved dashboard layouts
- Mobile-friendly views
- Dashboard customization
- Export history
- Historical playback

---

# Version 0.7 — Automation

Objective

Reduce manual monitoring.

## Planned Features

- Scheduled reports
- Telegram improvements
- Discord integration
- Email notifications
- Webhooks
- Daily market summaries
- Automatic diagnostics

---

# Version 0.8 — Strategy Lab

Objective

Provide a research environment for testing mining strategies.

## Planned Features

- Historical replay
- Strategy simulation
- Parameter optimization
- Profitability comparison
- What-if analysis
- Strike replay

---

# Version 0.9 — Multi-Coin Platform

Objective

Generalize the analytics engine beyond Bitcoin Cash.

## Planned Coins

- Bitcoin
- Litecoin
- Dogecoin
- Kaspa
- Monero
- Additional SHA-256 compatible coins

---

# Version 1.0 — BCH Rental Intelligence Platform

Objective

Deliver a mature, production-ready decision-support platform.

## Characteristics

- Reliable
- Explainable
- Self-monitoring
- Self-healing
- Extensible
- Production-ready
- Well documented
- Fully tested
- Easy to deploy
- Easy to maintain

---

# Future Ideas

Potential long-term additions.

## Analytics

- Machine learning forecasting
- Market anomaly detection
- Adaptive Opportunity Score
- Multi-factor confidence scoring

## Dashboard

- Live charts
- Historical playback
- Heat maps
- Opportunity timeline
- Advanced analytics

## Integrations

- Additional mining marketplaces
- Additional exchanges
- Mining pool APIs
- Mobile application

## Operations

- Automatic backups
- Archive management
- Cloud synchronization
- Remote monitoring

---

# Guiding Principles

Every feature should improve one or more of the following:

## Recommendation Quality

Produce more accurate and actionable rental recommendations.

## Explainability

Every recommendation should clearly explain why it was generated.

## Reliability

The engine should run unattended for extended periods while recovering gracefully from failures.

## Operator Experience

Present complex mining analytics through a simple and intuitive interface.

## Maintainability

Keep the architecture modular, well-tested, and easy to extend.

## Performance

Optimize execution time, storage efficiency, and resource usage.

## Privacy

Store only the information required for analysis.

Never collect wallet information, private keys, or personal user data.

---

# Engineering Workflow

Every feature follows the same development process.

```
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

# Long-Term Vision

The BCH Rental Engine has evolved from a simple probability calculator into a comprehensive mining decision-support platform.

Future development will continue focusing on:

- Better recommendations
- Better explanations
- Better analytics
- Better forecasting
- Better reliability
- Better operator experience

The long-term objective is to build a platform that miners trust—not because it predicts the future perfectly, but because every recommendation is transparent, explainable, and backed by measurable evidence.