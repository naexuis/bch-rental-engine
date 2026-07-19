# Architecture Guide

The BCH Rental Engine is a modular decision-support platform designed to evaluate short-duration Bitcoin Cash solo mining opportunities.

Rather than acting as an automated trading or mining system, the engine continuously analyzes the mining market, estimates expected outcomes under thousands of potential rental scenarios, and recommends whether a rental opportunity is economically attractive.

The system is intentionally composed of loosely coupled components that communicate primarily through JSON and SQLite, making it portable, easy to debug, and straightforward to deploy on a single Linux server.

---

# Design Philosophy

The project was designed around several guiding principles.

## Simplicity

The engine should run on a single computer without requiring external databases, web servers, or cloud infrastructure.

## Portability

The project should run equally well on:

- Umbrel
- Ubuntu
- AWS EC2
- DigitalOcean
- Linode
- Raspberry Pi
- Local workstation

without code changes.

## Transparency

Every recommendation should be explainable.

Rather than returning only a recommendation such as

```
RENT
```

the engine provides

- Expected Profit
- Risk Adjusted ROI
- Fair Value Ratio
- Block Probabilities
- Opportunity Score
- Market Regime

allowing the user to understand exactly why the recommendation was made.

## Modularity

Each subsystem has a single responsibility.

Examples include:

- Market Data
- Pool Adapters
- Optimization Engine
- Decision Engine
- Dashboard
- Telegram
- History Database

This makes future expansion significantly easier.

---

# High-Level Architecture

```text
                 CoinGecko
                     │
                     ▼
             Market Data Layer
                     │
                     ▼
             BCH Rental Engine
                     │
     ┌───────────────┼────────────────┐
     │               │                │
     ▼               ▼                ▼
 Latest JSON     SQLite History    JSONL Logs
     │
     ▼
 Streamlit Dashboard
     │
     ▼
 Decision Support
```

---

# Major Components

## 1. Market Data Layer

Purpose

Retrieve the current state of the BCH mining market.

Sources include

- CoinGecko
- Braiins
- MiningRigRentals
- BCH Network

Outputs

- BTC price
- BCH price
- BCH difficulty
- Estimated network hashrate
- Rental pricing
- Available hashrate

---

## 2. Pool Adapter Layer

Purpose

Provide a common interface for multiple rental providers.

Current adapters

- Braiins
- MiningRigRentals

Future adapters

- NiceHash
- Kryptex
- Additional marketplaces

Each adapter converts provider-specific APIs into a standardized internal format.

---

# 3. Optimization Engine

Purpose

Evaluate every feasible rental scenario.

Inputs

- Budget range
- Hashrate range
- Rental prices
- Market data

For each scenario the engine computes

- Rental duration
- Expected blocks
- P(0)
- P(1+)
- P(2+)
- Revenue
- Profit
- ROI

The engine may evaluate hundreds or thousands of scenarios during a single execution.

---

# 4. Decision Engine

The Decision Engine converts raw optimization results into actionable recommendations.

Metrics considered include

- Fair Value Ratio
- Risk-adjusted ROI
- Probability of success
- Market regime

Outputs

- RENT
- WATCH
- DO NOT RENT

along with an Opportunity Score.

---

# 5. Opportunity Score

Rather than relying on a single metric, the engine combines multiple indicators.

Current components

- Fair Value Ratio
- Risk-adjusted ROI
- Block probability
- Market regime

Result

```
0–100
```

Higher scores indicate better opportunities.

---

# 6. Pool Routing Engine

Once the optimal rental has been selected, the Pool Routing Engine determines the most appropriate mining pool.

Factors considered

- Existing pool hashrate
- Pool fee
- Network share
- Routing score

Output

Recommended pool along with ranked alternatives.

---

# 7. Historical Database

Historical recommendations are stored in SQLite.

Why SQLite?

- Zero administration
- Single file
- Portable
- Fast
- Excellent analytical performance

The database enables

- Historical charts
- Trend analysis
- Strategy evaluation
- Future backtesting

---

# 8. JSON State File

Each engine execution writes a complete snapshot of the current recommendation.

```
state/
    bch_solo_rental_strike_engine.json
```

Purpose

Provide a simple interface between

Engine

↓

Dashboard

The dashboard never runs the optimization itself.

It simply visualizes the latest engine output.

---

# 9. JSONL Logs

Operational events are written as JSON Lines.

Benefits

- Easy debugging
- Machine readable
- Incremental append
- Low overhead

Automatic log rotation prevents unlimited growth.

---

# 10. Streamlit Dashboard

The dashboard provides an operational interface.

Pages currently include

- Market Overview
- Decision Center
- Strike Analysis
- Pool Routing
- Historical Performance
- Candlestick Charts

The dashboard reads

- JSON state
- SQLite history

It performs no optimization itself.

---

# 11. Telegram Alerts

The alert subsystem monitors recommendation changes.

Notifications include

- Recommendation
- Opportunity Score
- Expected Profit
- Market Regime

Alerts are only sent when meaningful changes occur.

---

# Data Flow

```text
Market APIs
      │
      ▼
Market Data Layer
      │
      ▼
Optimization Engine
      │
      ▼
Decision Engine
      │
      ├────────────┐
      ▼            ▼
SQLite        JSON State
      │            │
      ▼            ▼
Dashboard    Telegram
```

---

# Why JSON + SQLite?

The project intentionally separates

Current State

↓

Historical State

The latest recommendation is stored in JSON because

- Simple
- Human readable
- Easy to inspect
- Fast

Historical information is stored in SQLite because

- Efficient queries
- Time-series analysis
- Reliable persistence

This combination keeps the system simple while providing robust historical capabilities.

---

# Why Streamlit?

The dashboard was built with Streamlit because

- Minimal infrastructure
- Rapid development
- Native Plotly integration
- Excellent data visualization
- Easy deployment

The goal is operational monitoring rather than a multi-user web application.

---

# Why Docker?

Docker provides

- Reproducible deployments
- Dependency isolation
- Easy upgrades
- Consistent runtime environment

The dashboard is currently deployed in Docker while the engine runs directly on the host.

This architecture allows the dashboard to be restarted independently of the engine.

---

# Why Umbrel?

The project originated on an Umbrel server because it provides

- Always-on operation
- Low power consumption
- Docker support
- Linux compatibility

However, the architecture is intentionally cloud-portable.

Supported deployment targets include

- AWS EC2
- Azure
- DigitalOcean
- Linode
- Vultr

---

# Future Architecture

The next major architectural additions include

- Technical Analysis Engine
- Historical Strategy Backtesting
- Dashboard Settings Editor
- Automated Rental Execution
- Multi-Coin Support
- AI Decision Assistant

These features will be added as separate modules to preserve the project's modular architecture.

---

# Architectural Principles

The project follows several long-term principles.

- Keep components loosely coupled.
- Separate computation from visualization.
- Prefer configuration over hardcoded values.
- Minimize external dependencies.
- Favor portable technologies.
- Record every recommendation for future analysis.
- Design for explainability rather than black-box decisions.

---

# Next Steps

Continue with:

- [Operations Runbook](OPERATIONS.md)
- [Deploy to EC2](DEPLOY_EC2.md)
- [Decision Log](DECISION_LOG.md)
- [Developer Journal](DEVELOPER_JOURNAL.md)