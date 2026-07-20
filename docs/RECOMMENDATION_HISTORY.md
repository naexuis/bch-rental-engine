# Recommendation History

## Purpose

The Recommendation History system records every execution of the BCH Rental Engine and provides a complete historical record of the engine's decision-making process.

Rather than only recording the final recommendation, the system captures every stage of the engine's decision pipeline, allowing operators to understand:

- What recommendation was produced
- Why that recommendation was produced
- How the underlying market conditions evolved
- How the engine's confidence changed over time
- Whether market conditions are improving or deteriorating

Recommendation History is intended to improve operational awareness, explainability, trend analysis, future model validation, and historical research.

---

# Design Goals

The Recommendation History system should:

- Record every engine execution.
- Preserve the complete engine decision pipeline.
- Capture meaningful recommendation changes.
- Preserve market and strike metrics.
- Support historical filtering.
- Support dashboard visualization.
- Support explainability.
- Support future machine learning and backtesting.
- Minimize storage requirements.
- Remain backward compatible as new fields are added.
- Be resilient to engine restarts.

---

# Philosophy

Recommendation History records the engine's decisions rather than every raw API response.

The objective is to reconstruct exactly how the engine arrived at a recommendation at any point in time.

Every historical record should answer:

- What did the engine know?
- What decision did the engine make?
- Why did the engine make that decision?
- How did that decision differ from previous runs?

---

# Core Concepts

Recommendation History is built around two complementary concepts.

## Snapshot

A Snapshot records the complete state of the BCH Rental Engine after every execution.

Every engine run creates exactly one Snapshot regardless of whether the recommendation changes.

Snapshots support:

- Historical reporting
- Trend analysis
- Dashboard visualizations
- Time-series analysis
- Machine learning
- Backtesting

Example

```
09:00

WATCH

09:15

WATCH

09:30

WATCH

09:45

WATCH

10:00

RENT
```

---

## Event

An Event represents a meaningful change between two Snapshots.

Events are derived dynamically by comparing adjacent history records rather than stored separately.

Typical Events include:

- Operator recommendation changed
- Opportunity Action changed
- Market Regime changed
- Recommended Pool changed
- Opportunity Score crossed a threshold
- Strike economics materially improved
- Fair Value Ratio crossed a threshold

Events support:

- Recommendation Change Log
- Notifications
- Explainability
- Operational review

Example

```
10:00 UTC

WATCH → RENT

Reason

Opportunity Score increased

Fair Value Ratio crossed threshold

Rental premium improved
```

---

# Engine Decision Pipeline

Every engine execution produces four progressively higher-level decisions.

## 1. Opportunity Score

A numerical score between 0 and 100 representing the attractiveness of the current rental opportunity.

Example

```
69.0
```

---

## 2. Opportunity Action

A qualitative interpretation of the Opportunity Score.

Possible values:

- STRIKE_NOW
- STRONG_WATCH
- WATCH
- WEAK_WATCH
- WAIT

This represents the engine's internal confidence.

---

## 3. Alert Tier

An internal classification used by the alerting system.

Examples include:

- DEPLOY_NOW
- STRONG_RENT
- NEAR_STRIKE
- WATCH_IMPROVING

Alert Tiers determine notification behavior and recommendation severity.

---

## 4. Operator Recommendation

The simplified recommendation presented to the operator.

Possible values:

- RENT
- NEAR STRIKE
- WATCH
- DO NOT RENT

This is the highest-level decision exposed by the dashboard.

---

# Historical Record

Each Snapshot records the complete engine state.

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
- Hashrate
- Duration
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
- Rental Premium / Discount
- Market Regime

---

## Pool Recommendation

- Recommended Pool
- Pool Routing Score

---

## Engine Metrics

- Confidence
- Opportunity Score
- Risk Score
- Scenario Count

---

# Success Criteria

The Recommendation History system should allow an operator to:

- Understand the complete engine decision process.
- View historical recommendations.
- Detect recommendation changes.
- Understand why recommendations changed.
- Compare recommendations across time.
- Review recommendation stability.
- Analyze long-term trends.
- Export historical data.
- Support future explainability.

---

# Engine History Dashboard

## Primary User Experience

The Engine History dashboard should answer five questions immediately.

1. What is the engine recommending now?
2. Has that recommendation changed?
3. Is the opportunity improving or deteriorating?
4. How confident is the engine becoming?
5. How frequently do actionable opportunities occur?

The page should emphasize decision evolution rather than raw historical data.

---

# Dashboard Layout

```
History Summary

↓

Operator Recommendation Timeline

↓

Opportunity Action Timeline

↓

Recommendation Change Log

↓

Decision Metric Trends

↓

Historical Run Details
```

---

# 1. History Summary

Display:

Current Recommendation

Current Opportunity Action

Current Opportunity Score

Current Market Regime

Time in Current Recommendation

Last Recommendation Change

Recommendation Changes

RENT Signals

WATCH Signals

DO NOT RENT Signals

---

# 2. Operator Recommendation Timeline

Displays:

- RENT
- NEAR STRIKE
- WATCH
- DO NOT RENT

This timeline reflects what the operator was advised to do.

---

# 3. Opportunity Action Timeline

Displays:

- STRIKE_NOW
- STRONG_WATCH
- WATCH
- WEAK_WATCH
- WAIT

This timeline reflects how the engine's internal confidence evolved even when the operator recommendation remained unchanged.

---

# 4. Recommendation Change Log

Records meaningful transitions between adjacent Snapshots.

Each entry includes:

- Timestamp
- Previous Recommendation
- New Recommendation
- Previous Opportunity Action
- New Opportunity Action
- Previous Market Regime
- New Market Regime
- Opportunity Score Change
- Fair Value Ratio Change
- Expected ROI Change
- Primary Decision Driver

---

# 5. Decision Metric Trends

Charts include:

- Opportunity Score
- Confidence
- Fair Value Ratio
- Rental Premium
- Risk-Adjusted ROI
- Probability of Success
- BCH Price
- BTC Price
- Network Difficulty

Recommendation transitions should be highlighted on each chart.

---

# 6. Historical Run Details

The complete history table should include:

- Timestamp
- Operator Recommendation
- Opportunity Action
- Alert Tier
- Opportunity Score
- Market Regime
- Budget
- Hashrate
- Duration
- Probability
- Expected Profit
- Expected ROI
- Fair Value Ratio
- Rental Premium
- Recommended Pool

Supported functionality:

- Date filtering
- Recommendation filtering
- Market filtering
- Sorting
- CSV Export

---

# Default Time Range

Default:

30 Days

Available ranges:

- 24 Hours
- 3 Days
- 7 Days
- 30 Days
- 90 Days
- All History

---

# Future Enhancements

Future capabilities may include:

- Recommendation Stability Index
- Confidence Trend Analysis
- Decision Driver Analytics
- Historical Replay Mode
- Strategy Backtesting
- Machine Learning Feature Generation
- Recommendation Forecasting
- Notification History
- Multi-Coin Recommendation Comparison
- Engine Performance Benchmarking