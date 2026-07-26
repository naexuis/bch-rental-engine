# Recommendation History

## Purpose

Recommendation History is the historical intelligence subsystem of the BCH Rental Engine.

Every execution of the engine produces a complete Snapshot of the market, the engine's decision pipeline, and the supporting analytics. These Snapshots allow the engine to explain not only **what** recommendation was produced, but **why**, **how**, and **how the recommendation is evolving over time**.

Rather than simply storing historical recommendations, Recommendation History provides the foundation for:

- Explainability
- Trend Intelligence
- Operational awareness
- Dashboard analytics
- Future forecasting
- Strategy backtesting
- Machine learning
- Historical research

The system enables operators to answer questions such as:

- What recommendation was produced?
- Why was it produced?
- What changed since the previous execution?
- Is the opportunity improving or deteriorating?
- How confident is the engine becoming?
- Is the trend accelerating or slowing?
- What conditions are preventing a better recommendation?

---

# Design Goals

Recommendation History is designed to be:

- Complete
- Explainable
- Deterministic
- Compact
- Backward compatible
- Extensible
- Analytics friendly
- Dashboard friendly
- Machine learning friendly

Every engine execution should be reproducible from the stored history.

---

# Core Philosophy

The BCH Rental Engine is a decision-support system.

Recommendation History therefore records **decisions**, not raw API responses.

The objective is to preserve everything necessary to reconstruct exactly how the engine reached a recommendation without storing unnecessary transient data.

Each historical record should answer:

- What market existed?
- What did the engine observe?
- What recommendation was produced?
- Why?
- How has the recommendation evolved?

---

# Architecture

```
Engine Execution
        │
        ▼
Snapshot Created
        │
        ▼
SQLite History
        │
        ▼
History Retrieval API
        │
        ▼
Analytics Framework
        │
        ▼
Dashboard
        │
        ▼
Operator
```

Recommendation History is now the data source for the engine's analytics framework.

---

# Historical Snapshot

Every engine execution creates exactly one immutable Snapshot.

Snapshots are never modified after insertion.

Each Snapshot records:

## Metadata

- Timestamp
- Engine Version
- Git Commit
- Dashboard Version

---

## Decision Pipeline

- Opportunity Score
- Opportunity Action
- Alert Tier
- Operator Recommendation

---

## Strike Recommendation

- Budget
- Rental Duration
- Recommended Hashrate
- Probability of Success
- Expected Revenue
- Expected Profit
- Expected ROI
- Risk-Adjusted ROI

---

## Market Snapshot

- BCH Price
- BTC Price
- BCH/BTC Ratio
- Network Difficulty
- Network Hashrate
- Fair Value Ratio
- Rental Premium
- Market Regime

---

## Pool Recommendation

- Recommended Pool
- Pool Routing Score

---

## Engine Metrics

- Scenario Count
- Confidence
- Risk Score

Snapshots intentionally contain enough information to recreate the engine's recommendation at any point in time.

---

# Events

Events are derived dynamically by comparing adjacent Snapshots.

Events are not stored separately.

Examples include:

- Recommendation changed
- Opportunity Action changed
- Market Regime changed
- Pool recommendation changed
- Opportunity Score crossed a threshold
- Fair Value Ratio crossed a threshold
- Strike economics materially improved
- Trend strength changed

Events support:

- Notifications
- Dashboard timelines
- Change logs
- Explainability
- Forecasting

---

# Analytics Framework

Recommendation History now powers the reusable analytics subsystem.

```
SQLite History
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
        ├──────────────┐
        ▼              ▼
Confidence     Persistence
        │              │
        └──────┬───────┘
               ▼
           Velocity
               │
               ▼
          Volatility
               │
               ▼
        Trend Strength
               │
               ▼
        Interpretation
               │
               ▼
        Dashboard / API
```

The analytics framework is generic and can analyze any numeric metric stored in Recommendation History.

---

# Current Analytics

The engine currently computes:

## Trend Direction

- IMPROVING
- DECLINING
- STABLE

---

## Confidence

- HIGH
- MEDIUM
- LOW

Confidence considers:

- Number of observations
- Trend consistency
- History depth

---

## Persistence

Measures the number of consecutive movements in the same direction.

Examples:

- 1 improvement
- 4 consecutive improvements
- 7 consecutive declines

---

## Velocity

Measures the average rate of change between observations.

Velocity provides early detection of rapidly improving or deteriorating conditions.

---

## Volatility

Classifies market stability.

Current levels:

- LOW
- HIGH

---

## Trend Strength

Current classifications:

- VERY_STRONG
- STRONG
- MODERATE
- UNKNOWN

Trend strength combines:

- Confidence
- Persistence
- Volatility
- Direction
- High-velocity promotion

---

# Explainability

Recommendation History provides the evidence used by the engine's explanation system.

Current explanations include:

- Recommendation reason
- Previous recommendation
- Score change
- Market blockers
- Conditions required to rent
- Trend interpretation
- Trend confidence
- Trend persistence
- Trend velocity
- Trend volatility
- Trend strength

Every explanation presented to the operator should be traceable to Recommendation History.

---

# Dashboard Vision

The Recommendation History dashboard should immediately answer:

1. What is the engine recommending?
2. Has that recommendation changed?
3. Is the opportunity improving?
4. How confident is the engine?
5. How strong is the trend?
6. How frequently do actionable opportunities occur?

The dashboard should emphasize decision evolution rather than raw historical data.

---

# Future Enhancements

Recommendation History is intended to support the next generation of analytics.

Planned capabilities include:

## Forecast Intelligence

- Trend acceleration
- Trend deceleration
- Trend reversal detection
- Plateau detection
- False trend detection
- Forecast confidence
- Early strike opportunity detection

---

## Historical Analytics

- Recommendation Stability Index
- Recommendation frequency
- Decision Driver Analytics
- Market health scoring
- Historical replay
- Strategy backtesting
- Forecast validation

---

## Dashboard Enhancements

- Historical playback
- Interactive timelines
- Recommendation heat maps
- Trend explorer
- Multi-metric overlays
- Decision drill-down
- Exportable analytics

---

# Long-Term Vision

Recommendation History has evolved from a simple audit log into the historical intelligence layer of the BCH Rental Engine.

Every future analytics feature—including forecasting, strategy simulation, machine learning, and explainable AI—will build upon this subsystem.

The long-term objective is to provide operators with complete transparency into not only **what** the engine recommends, but **how**, **why**, and **where those recommendations are likely headed next**.