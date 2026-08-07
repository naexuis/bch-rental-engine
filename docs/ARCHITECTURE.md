# BCH Rental Engine
# Architecture Guide

**Architecture Revision:** 3.0

**Application Release:** 0.1.x

**Architecture Status:** Stable (Canonical Decision Architecture)

---

# Purpose

The BCH Rental Engine is an explainable decision-support platform for evaluating Bitcoin Cash solo-mining rental opportunities.

Unlike traditional mining calculators that simply estimate mining profitability, the BCH Rental Engine continuously evaluates market conditions, generates executable rental scenarios, produces a single canonical operator decision, explains the reasoning behind every recommendation, tracks historical changes, and presents actionable guidance to the operator.

The guiding philosophy of the project is simple:

> **Every recommendation should be transparent, explainable, reproducible, testable, and backed by measurable evidence.**

The engine is designed to answer four fundamental questions:

- Should I rent hashpower?
- Why was that recommendation made?
- What changed since the last analysis?
- What must improve before a stronger recommendation can be made?

---

# Design Principles

The BCH Rental Engine is built around seven architectural principles.

## 1. Single Source of Truth

Business decisions are made exactly once.

The engine contains a single **Canonical Decision Engine** that determines the operator recommendation.

Current outputs derived from the canonical decision include:

- Alert Tier
- Recommendation
- Opportunity Action
- Dashboard presentation

Additional consumers (history persistence and notifications) will migrate to the canonical decision over time while maintaining backward compatibility.

---

## 2. Explainability

Operators should never have to trust a black box.

Every recommendation should explain:

- Why it was produced
- Current Opportunity Score
- Canonical Decision
- Market Regime
- Historical trend
- Current blockers
- Supporting economic metrics

---

## 3. Separation of Responsibilities

Every subsystem performs one responsibility.

```
Market Data

↓

Scenario Generation

↓

Canonical Decision

↓

Persistence

↓

Analytics

↓

Presentation

↓

Operator
```

This layered architecture allows each subsystem to evolve independently.

---

## 4. Test-Driven Development

Every architectural change follows the same engineering workflow.

```
Design

↓

Tests

↓

Implementation

↓

Compile

↓

Regression Tests

↓

Commit

↓

Push

↓

Release
```

Architecture changes are introduced incrementally and validated with automated regression testing.

---

## 5. Portability

The engine is designed to run from the same codebase on multiple platforms.

Supported environments include:

- Umbrel
- Ubuntu
- Docker
- Raspberry Pi
- AWS
- DigitalOcean
- Local Linux Workstations

---

## 6. Backward Compatibility

Major architectural improvements are introduced without breaking existing deployments.

Compatibility layers remain in place until all downstream consumers have migrated.

---

## 7. Explainable Intelligence

Analytics should improve operator understanding—not replace it.

Every recommendation should be reproducible from measurable data.

---

# High-Level Architecture

```
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
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
  Alert Tier     Recommendation    Opportunity Action
                         │
                         ▼
                Persistence Layer
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 SQLite History     JSON State      JSONL Logs
                         │
                         ▼
                 Analytics Layer
                         │
                         ▼
              Explainability Layer
                         │
                         ▼
 Dashboard • Notifications • CLI
```

---

# Repository Structure

```
bch-rental-engine/

├── config/
├── dashboard/
├── docs/
├── logs/
├── scripts/
├── state/
├── tests/
├── Dockerfile
├── Dockerfile.dashboard
└── docker-compose.yml
```

The repository is organized so that each major subsystem is isolated from the others.

---

# Architectural Layers

## Layer 1 — Market Data

Purpose:

Collect the current Bitcoin Cash mining environment.

Current providers include:

- CoinGecko
- Braiins Hashpower
- MiningRigRentals
- BCH Network

Current outputs include:

- BCH price
- BTC price
- Network difficulty
- Network hashrate
- Rental pricing
- Available rental hashrate

---

## Layer 2 — Scenario Generation

Purpose:

Generate every executable rental scenario within the configured operational constraints.

Each scenario evaluates:

- Budget
- Rental source
- Rental duration
- Hashrate
- Expected blocks
- Expected revenue
- Expected profit
- Risk-adjusted ROI
- Fair Value Ratio
- Probability of finding one or more blocks

Only executable scenarios continue into the Canonical Decision Engine.

---

## Layer 3 — Canonical Decision Engine

The Canonical Decision Engine is the heart of the BCH Rental Engine.

Every operator recommendation originates from a single function:

```
determine_canonical_decision()
```

Current canonical decisions are:

```
RENT_NOW

READY

WATCH_CLOSELY

WATCH

WAIT

UNAVAILABLE
```

The Canonical Decision Engine evaluates:

- Fair Value Ratio
- Risk-adjusted ROI
- Probability thresholds
- Scenario executability

No other subsystem independently determines whether the operator should rent.

For implementation details, see:

```
docs/RECOMMENDATION_DECISION_MODEL.md
```

---

## Layer 4 — Compatibility Layer

Legacy interfaces are currently derived from the Canonical Decision.

Current compatibility outputs include:

- Alert Tier
- Recommendation
- Opportunity Action

This compatibility layer allows the internal architecture to evolve while preserving existing APIs, dashboards, and historical data.

---

## Layer 5 — Opportunity Scoring

The Opportunity Score measures **opportunity attractiveness**, not operator guidance.

Current scoring inputs include:

- Fair Value Ratio
- Probability
- Risk-adjusted ROI
- Market Regime

Current output:

```
Opportunity Score
```

The Opportunity Score supports decision making but does **not** determine the recommendation.

The recommendation is determined exclusively by the Canonical Decision Engine.

---

## Layer 6 — Persistence

The engine maintains three independent persistence mechanisms.

### SQLite

Long-term historical storage.

### JSON

Current engine state.

### JSONL

Operational logs.

Each persistence mechanism serves a different operational purpose.

Future releases will continue migrating additional canonical decision information into historical storage while maintaining backward compatibility.

---

## Layer 7 — Analytics

Historical information is converted into reusable analytical primitives.

Current capabilities include:

- Historical retrieval
- Numeric trends
- Trend strength
- Trend persistence
- Opportunity Score changes
- Recommendation changes

Analytics functions are intentionally generic and reusable.

---

## Layer 8 — Explainability

Purpose:

Transform analytical results into operator-facing explanations.

Current explanations include:

- Recommendation reasoning
- Opportunity history
- Trend analysis
- Score limiters
- Economic blockers

The Explainability Layer answers:

- What changed?
- Why did it change?
- What is preventing a stronger recommendation?
- What conditions must improve before renting?

---

## Layer 9 — Presentation

Presentation layers consume engine outputs.

Current presentation layers include:

- Streamlit Dashboard
- Command Line Interface (CLI)

Current integrations under migration include:

- Telegram Notifications
- Future Discord Notifications

Presentation layers do **not** contain business decision logic.

---

# Current Data Flow

```
Market APIs
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
      ├────────► Opportunity Action
      │
      ▼
Persistence
      │
      ▼
Analytics
      │
      ▼
Explainability
      │
      ▼
Dashboard / CLI / Notifications
```

---

# Documentation Map

The BCH Rental Engine documentation is organized into focused documents.

| Document | Purpose |
|----------|---------|
| **ARCHITECTURE.md** | High-level system architecture |
| **RECOMMENDATION_DECISION_MODEL.md** | Canonical Decision Engine design |
| **RECOMMENDATION_HISTORY.md** | Historical recommendation storage |
| **UMBREL_RELEASE_PROCESS.md** | Production release workflow |
| **INSTALL.md** | Installation instructions |
| **CONFIGURATION.md** | Runtime configuration |
| **OPERATIONS.md** | Day-to-day operational procedures |
| **ROADMAP.md** | Planned features and future milestones |
| **CHANGELOG.md** | Release history |
| **DECISION_LOG.md** | Major architectural decisions |

Each subsystem should have one authoritative document.

ARCHITECTURE.md serves as the high-level entry point into the project documentation.

---

# Testing Architecture

The BCH Rental Engine uses layered automated testing.

Current coverage includes:

- Recommendation Logic
- Canonical Decision Engine
- Opportunity Scoring
- Recommendation History
- Trend Intelligence
- Dashboard Decision Mapping
- Explainability
- Historical Analytics

Current status:

```
125+ Automated Tests
```

Every architectural layer is protected by automated regression tests.

---

# Release Architecture

Application releases follow the documented production workflow.

```
Development Repository
        │
        ▼
Production Umbrel Build
        │
        ▼
Docker Image
        │
        ▼
GitHub Container Registry (GHCR)
        │
        ▼
Umbrel App Store Repository
        │
        ▼
Umbrel Installation
```

The complete release procedure is documented in:

```
docs/UMBREL_RELEASE_PROCESS.md
```

---

# Current Architecture Status

The current architecture includes:

- ✅ Market Data Layer
- ✅ Scenario Generation Engine
- ✅ Canonical Decision Engine
- ✅ Compatibility Layer
- ✅ Opportunity Scoring
- ✅ Persistence Layer
- ✅ Analytics Layer
- ✅ Explainability Layer
- ✅ Streamlit Dashboard
- ✅ Native Umbrel Deployment
- ✅ Automated Test Suite

Current architecture is considered stable.

---

# Future Architecture

Planned architectural additions include:

- Canonical Decision persistence
- Decision Confidence model
- Notification migration
- Historical decision analytics
- Trend forecasting
- Volatility analysis
- Autonomous strike detection
- Strategy simulation

Future capabilities should extend the existing layered architecture rather than introducing parallel decision systems.

---

# Long-Term Vision

The BCH Rental Engine has evolved from a mining profitability calculator into a complete decision-support platform.

The long-term objective is to build a system that operators trust because every recommendation is:

- Transparent
- Explainable
- Reproducible
- Testable
- Historically traceable
- Operationally actionable

Future development will continue to emphasize:

- Simplicity
- Modularity
- Architectural consistency
- Explainable analytics
- Historical intelligence
- Decision quality
- Operational reliability

Every new capability should strengthen the existing architecture rather than increase complexity.