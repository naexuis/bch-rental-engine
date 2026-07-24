# BCH Rental Engine Roadmap

The BCH Rental Engine is an actively evolving decision-support platform for evaluating Bitcoin Cash hashpower rental opportunities.

Rather than attempting to predict the future, the engine focuses on producing transparent, explainable, and data-driven recommendations that help operators decide:

> **"Should I rent hashpower right now?"**

The long-term goal is to become the most comprehensive open-source analytics platform for cryptocurrency hashpower rentals.

---

# Current Version

**Version:** v2.3.0

**Release:** Trend Intelligence

**Status:** Active Development

---

# Project Vision

The BCH Rental Engine combines:

- Live market pricing
- Network conditions
- Rental pricing
- Statistical probability
- Risk-adjusted profitability
- Historical intelligence
- Trend analysis
- Explainable decision logic
- Operational tooling

The objective is not to automate mining decisions, but to explain them.

Every recommendation should answer:

- What should I do?
- Why?
- What changed?
- What is preventing a better recommendation?
- Which direction are market conditions moving?

---

# System Architecture

```
Market Data
      │
      ▼
Opportunity Scoring
      │
      ▼
Recommendation Engine
      │
      ▼
History Persistence
      │
      ▼
History Retrieval API
      │
      ▼
Analytics Layer
      │
      ▼
Explainability
      │
      ▼
Operator
```

---

# Development Phases

## Phase 1 — Core Engine ✅

Status: Complete

### Completed

- Live BCH market data
- BCH difficulty tracking
- Network hashrate estimation
- Braiins Hashpower integration
- MiningRigRentals integration
- Budget optimization
- Hashrate optimization
- Strike scoring
- Opportunity scoring
- Market regime classification
- Pool routing engine
- Telegram alerts
- SQLite history
- JSON state output
- Streamlit dashboard
- Docker deployment
- Candlestick charts
- Automatic JSONL log rotation
- Comprehensive documentation

---

## Phase 2 — Decision Intelligence ✅

Status: Complete

Major additions

- Opportunity Score
- Opportunity Actions
- Economic score caps
- Market regime classification
- Probability target alignment
- Dedicated Opportunity Score test suite
- Characterization tests
- Score calibration

---

## Phase 3 — Historical Intelligence ✅

Status: Complete

Features

- Recommendation History
- Previous Opportunity Action
- Previous Opportunity Score
- Opportunity Score delta
- Action normalization
- Action transition detection
- Upgrade / Downgrade classification
- SQLite history API
- Generic history retrieval

---

## Phase 4 — Explainability ✅

Status: Complete

Features

- Opportunity History
- Score Limiter
- Market blockers
- Conditions needed to rent
- Transparent recommendation reasoning
- Recommendation explanation improvements

---

## Phase 5 — Trend Intelligence ✅

Status: Complete

Features

- Generic numeric trend engine
- Generic metric trend engine
- Opportunity Score trend analysis
- Trend presentation helper
- Trend unit test suite
- Analytics layer architecture

Current output includes

- Direction
- Previous score
- Current score
- Latest change
- History depth

---

## Phase 6 — Trend Confidence 🚧

Status: Next

Goal

Improve trust in trend analysis.

Planned

- Trend confidence score
- Consecutive improvement detection
- Consecutive decline detection
- Minimum history requirements
- Trend quality scoring
- Plateau detection
- False trend detection

Example

```
Trend

Direction:
IMPROVING

Confidence:
HIGH

Reason:
18 observations
5 consecutive improvements
```

---

## Phase 7 — Volatility Intelligence

Status: Planned

Goal

Understand market stability.

Features

- Opportunity Score volatility
- FVR volatility
- ROI volatility
- BCH price volatility
- Difficulty volatility
- Stable vs unstable market detection
- Opportunity stability score

---

## Phase 8 — Forecasting

Status: Planned

Goal

Estimate where the market is heading.

Potential features

- Rolling averages
- Exponential moving averages
- Opportunity Score forecasting
- Difficulty forecasting
- Rental price forecasting
- Time-to-strike estimation
- Expected recommendation transitions

---

## Phase 9 — Autonomous Strike Detection

Status: Planned

Goal

Detect high-quality rental opportunities automatically.

Possible features

- Automatic strike alerts
- Opportunity ranking
- Opportunity confidence
- Market health score
- Strike countdown
- Opportunity expiration estimates

---

## Phase 10 — Dashboard Intelligence

Status: Planned

Future dashboard additions

- Trend dashboard
- Opportunity timeline
- Volatility dashboard
- Confidence indicators
- Recommendation history charts
- Score distribution charts
- Trend explorer
- Historical playback

---

## Phase 11 — Historical Analytics

Status: Planned

Features

- Recommendation performance
- Historical Opportunity Score distributions
- ROI distributions
- FVR distributions
- Recommendation frequency
- Historical market statistics
- Long-term analytics

---

## Phase 12 — Strategy Backtesting

Status: Planned

Features

- Replay historical markets
- Strategy simulation
- Profitability curves
- Strategy comparison
- Parameter optimization
- Historical strike replay

---

## Phase 13 — Automation

Status: Planned

Features

- Scheduled engine execution
- Automatic updates
- Health monitoring
- Scheduled reports
- Email alerts
- Discord
- Slack
- SMS

---

## Phase 14 — Multi-Coin Support

Status: Planned

Potential additions

- Bitcoin
- Litecoin
- Dogecoin
- Kaspa
- Monero

Goal

Generalize the analytics engine beyond BCH.

---

## Phase 15 — Predictive Decision Engine

Status: Long-Term Vision

Long-term capabilities

- Predictive Opportunity Score
- Predictive recommendations
- Machine-assisted forecasting
- Intelligent market summaries
- Interactive operator assistant
- Daily market brief
- Explainable AI recommendations

---

# Analytics Layer

The analytics layer is now a reusable subsystem.

```
SQLite
     │
     ▼
History Retrieval
     │
     ▼
Metric Trend
     │
     ▼
Numeric Trend
     │
     ▼
Presentation
```

Future analytics will reuse this architecture.

---

# Testing Philosophy

Every feature follows the same development workflow.

```
Design

↓

Tests

↓

Implementation

↓

Compile

↓

Runtime Validation

↓

Full Regression Suite

↓

Commit

↓

Push

↓

Release Tag
```

This workflow has become one of the core engineering principles of the project.

---

# Release History

| Version | Major Capability |
|----------|------------------|
| v1.0.0 | Dashboard Decision Center |
| v1.1.0 | Documentation & Changelog |
| v2.0.0 | Dashboard V2 Operator Console |
| v2.0.1 | Dashboard Polish |
| v2.1.0 | Operations Toolkit |
| v2.2.0 | Opportunity Intelligence & Explainability |
| v2.3.0 | Trend Intelligence |

---

# Guiding Principles

Every new feature should improve at least one of:

- Recommendation quality
- Explainability
- Reliability
- Testability
- Maintainability
- Performance
- Operator experience

Features that do not improve one of these goals should be carefully evaluated before implementation.

---

# Long-Term Vision

The BCH Rental Engine has evolved from a probability calculator into a layered decision-support platform.

Future work will continue to focus on:

- Better recommendations
- Better explanations
- Better historical intelligence
- Better analytics
- Better forecasting
- Better operational tooling

The long-term objective is to build a platform that operators trust—not because it predicts the future perfectly, but because every recommendation is transparent, explainable, and backed by measurable evidence.