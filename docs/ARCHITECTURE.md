# Architecture Guide

The BCH Rental Engine is a layered decision-support platform for evaluating Bitcoin Cash hashpower rental opportunities.

The engine is designed around one guiding principle:

> **Every recommendation should be transparent, explainable, testable, and backed by measurable evidence.**

Unlike traditional mining calculators, the BCH Rental Engine does not simply calculate profitability.

It explains:

- What should be done
- Why that recommendation was produced
- What changed since the previous execution
- Which market conditions are improving or deteriorating
- What is preventing a stronger recommendation

---

# Current Version

**Version:** v2.3.0

**Architecture Status:** Stable

---

# Design Philosophy

The BCH Rental Engine is built around six core principles.

## 1. Explainability

Every recommendation should be understandable.

The operator should never have to trust a black box.

Instead, the engine explains:

- Opportunity Score
- Recommendation
- Trend
- Score Limiter
- Historical changes
- Current blockers

---

## 2. Layered Architecture

Each architectural layer has a single responsibility.

```
Market Data

↓

Decision Engine

↓

History

↓

Analytics

↓

Explainability

↓

Operator
```

This separation allows each subsystem to evolve independently.

---

## 3. Modularity

Every subsystem should perform exactly one job.

Examples

- Market Data
- Opportunity Scoring
- Recommendation Engine
- History
- Analytics
- Dashboard
- Telegram

No subsystem should contain unrelated logic.

---

## 4. Testability

Every new capability follows the same engineering workflow.

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

Regression Tests

↓

Commit

↓

Push

↓

Release
```

This workflow has become a core architectural principle.

---

## 5. Portability

The engine runs on

- Umbrel
- Ubuntu
- Raspberry Pi
- AWS
- DigitalOcean
- Local Linux workstations

using the same codebase.

---

## 6. Explainable Intelligence

The engine favors transparent analytics over opaque prediction.

Every recommendation should be reproducible from the underlying data.

---

# High-Level Architecture

```
                    External APIs
                          │
                          ▼
                   Market Data Layer
                          │
                          ▼
                 Opportunity Scoring
                          │
                          ▼
                Recommendation Engine
                          │
        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼
  History Database    JSON State        JSONL Logs
        │
        ▼
    Analytics Layer
        │
        ▼
  Explainability Layer
        │
        ▼
 Dashboard / Telegram / Operator
```

---

# Layer 1 — Market Data

Purpose

Collect the current BCH mining environment.

Current sources

- CoinGecko
- Braiins Hashpower
- MiningRigRentals
- BCH Network

Outputs

- BTC price
- BCH price
- Difficulty
- Network hashrate
- Rental pricing
- Available hashrate

---

# Layer 2 — Opportunity Scoring

Purpose

Evaluate every feasible rental scenario.

Current scoring inputs

- Fair Value Ratio
- Risk-adjusted ROI
- Probability of finding a block
- Market Regime

Outputs

- Opportunity Score
- Opportunity Action

Economic caps ensure poor economics never appear attractive.

Current caps

```
FVR < 0.85

↓

Score capped at 39

FVR < 0.90

↓

Score capped at 49

ROI < -10%

↓

Score capped at 54

ROI < 0%

↓

Score capped at 69
```

---

# Layer 3 — Recommendation Engine

Purpose

Convert Opportunity Scores into operator recommendations.

Outputs

- RENT
- WATCH
- DO NOT RENT

Supporting classifications

- STRIKE_NOW
- STRONG_WATCH
- WATCH
- WEAK_WATCH
- WAIT

---

# Layer 4 — Historical Intelligence

Purpose

Persist every recommendation.

Storage

SQLite

Historical data includes

- Opportunity Score
- Opportunity Action
- Market Regime
- Recommendation
- ROI
- FVR
- Probability
- Difficulty
- Pricing

The history subsystem also tracks

- Previous Action
- Previous Opportunity Score
- Score Delta
- Action Classification

---

# Layer 5 — Analytics

The analytics layer converts historical data into reusable analytical primitives.

Current architecture

```
SQLite

↓

History Retrieval

↓

Metric Extraction

↓

Numeric Trend

↓

Trend Persistence
```

Current primitives

### History

```
get_history_rows()
```

### Numeric Trends

```
calculate_numeric_trend()
```

### Metric Trends

```
calculate_metric_trend()
```

### Trend Persistence

```
calculate_trend_persistence()
```

These functions are intentionally generic and reusable.

They are not BCH-specific.

---

# Layer 6 — Explainability

Purpose

Transform analytical results into operator-facing explanations.

Current presentation helpers

```
build_opportunity_history_section()

build_score_limiter_section()

build_opportunity_trend_section()
```

The engine now explains

- What changed
- Current trend
- Why the score is limited
- Market blockers
- Conditions required to rent

---

# Persistence Layer

Current State

```
state/

bch_solo_rental_strike_engine.json
```

Historical State

```
state/

bch_rental_history.sqlite
```

Operational Logs

```
logs/

*.jsonl
```

Each storage mechanism serves a different purpose.

---

# Dashboard

The dashboard performs no optimization.

Instead it consumes

- JSON State
- SQLite History

The engine remains the single source of truth.

---

# Telegram

Telegram notifications are intentionally lightweight.

Alerts summarize

- Recommendation
- Opportunity Score
- Market Regime
- Significant changes

Future versions will incorporate Trend Intelligence.

---

# Data Flow

```
Market APIs
      │
      ▼
Market Data
      │
      ▼
Opportunity Scoring
      │
      ▼
Recommendation Engine
      │
      ├─────────────┐
      ▼             ▼
SQLite        JSON State
      │             │
      ▼             ▼
Analytics     Dashboard
      │
      ▼
Explainability
      │
      ▼
Operator
```

---

# Testing Architecture

The project currently contains dedicated test suites for

- Recommendation History
- Opportunity Scoring
- Interpretation
- Trend Analytics

Regression tests currently validate

- Opportunity Scoring
- Recommendation History
- Trend Analysis
- Interpretation
- Explainability

Every architectural layer is protected by automated tests.

---

# Release Evolution

| Version | Major Architectural Addition |
|----------|------------------------------|
| v1.0 | Core Engine |
| v1.1 | Dashboard |
| v2.0 | Operator Console |
| v2.1 | Operations Toolkit |
| v2.2 | Opportunity Intelligence & Explainability |
| v2.3 | Trend Intelligence |

---

# Future Architecture

The next architectural additions will expand the Analytics Layer.

Planned

```
History

↓

Metric Analysis

↓

Trend

↓

Persistence

↓

Trend Confidence

↓

Volatility

↓

Forecasting

↓

Autonomous Strike Detection
```

Each capability will build on the previous layer rather than introducing unrelated functionality.

---

# Long-Term Vision

The BCH Rental Engine has evolved from a profitability calculator into a layered decision-support platform.

Future development will continue to prioritize

- Explainability
- Analytics
- Historical intelligence
- Trend analysis
- Forecasting
- Operational tooling

The long-term objective is not simply to predict profitable rentals.

The objective is to build a platform that operators trust because every recommendation is transparent, measurable, reproducible, and explainable.