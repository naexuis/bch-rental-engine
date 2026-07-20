# Recommendation History

## Purpose

The Recommendation History system records every execution of the BCH Rental Engine and provides historical visibility into how recommendations evolve over time.

Rather than only showing the current recommendation, Recommendation History enables operators to understand how the engine's decisions have changed, why they changed, and whether market conditions are improving or deteriorating.

The Recommendation History system is intended to improve explainability, operational confidence, trend analysis, and future model evaluation.

---

# Design Goals

The Recommendation History system should:

- Record every engine execution.
- Capture all recommendation changes.
- Preserve important decision metrics.
- Allow historical filtering.
- Support visual trend analysis.
- Support future machine learning and backtesting.
- Minimize storage requirements.
- Be resilient to engine restarts.

---

# Philosophy

Recommendation History records the engine's decisions rather than every piece of raw market data.

The goal is to reconstruct why the engine made a recommendation at a specific point in time.

Historical records should therefore emphasize:

- Recommendation
- Confidence
- Decision drivers
- Market state
- Strike recommendation
- Pool recommendation

instead of duplicating every API response received during execution.

---

# Core Concepts

The Recommendation History system is built around two complementary concepts:

## Snapshot

A Snapshot records the complete state of the BCH Rental Engine after every execution.

Every engine run creates exactly one Snapshot, regardless of whether the recommendation changed.

Snapshots provide the historical data used for:

- Trend analysis
- Time-series charts
- Historical comparisons
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

An Event records only meaningful changes in engine behavior.

Events are generated when one or more monitored conditions change.

Typical Events include:

- Recommendation changed
- Market State changed
- Recommended Pool changed
- Confidence crossed threshold
- Opportunity Score crossed threshold
- Strike Recommendation changed significantly

Events are intended for:

- Notifications
- Recommendation Change Log
- Explainability
- Operational review

Example

```
10:00

WATCH → RENT

Reason

Rental premium decreased

BCH price increased

FVR crossed threshold
```

---

## Relationship

Every engine execution creates a Snapshot.

Some Snapshots also generate one or more Events.

```
Engine Run

↓

Snapshot

↓

Did anything important change?

↓

YES

↓

Create Event

↓

Store Snapshot
```

---

# Historical Record

Each execution of the BCH Rental Engine generates a single historical record.

## Metadata

- Timestamp
- Engine Version
- Git Commit
- Dashboard Version

---

## Recommendation

- Recommendation
- Market State
- Confidence
- Recommendation Message

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
- Network Difficulty
- Network Hashrate
- Rental Price
- Fair Value Ratio (FVR)
- Rental Premium

---

## Pool Recommendation

- Recommended Pool
- Routing Score

---

## Decision Metrics

- Opportunity Score
- Risk Score

---

# Success Criteria

The Recommendation History system should allow an operator to:

- View historical recommendations.
- Understand why recommendations changed.
- Compare today's recommendation to previous days.
- Detect recommendation trends.
- Review recommendation stability.
- Support future analytics.
- Support explainability.

---

# Engine History Dashboard

## Primary User Experience

The Engine History page should answer five questions immediately.

1. What is the engine recommending now?
2. Has the recommendation recently changed?
3. Is the opportunity improving or deteriorating?
4. How stable has the recommendation been?
5. How often do profitable opportunities occur?

The page should prioritize recommendation changes and decision trends rather than displaying a raw database table.

---

# Dashboard Layout

```
History Summary

↓

Recommendation Timeline

↓

Recommendation Change Log

↓

Decision Metric Trends

↓

Historical Run Details
```

---

# 1. History Summary

The History Summary provides a high-level overview for the selected time period.

## Current Status

- Current Recommendation
- Current Market State
- Current Confidence

## Recommendation Activity

- Time in Current Recommendation
- Last Recommendation Change
- Number of Recommendation Changes

## Recommendation Distribution

- RENT Signals
- WATCH Signals
- DO NOT RENT Signals

Example

```
Current Recommendation

WATCH

Time in Current State

2 Days 6 Hours

Last Recommendation Change

DO NOT RENT → WATCH

Recommendation Changes

3

RENT Signals

1
```

---

# 2. Recommendation Timeline

The Recommendation Timeline displays every engine execution over time.

Each recommendation is represented by one of three states:

- RENT
- WATCH
- DO NOT RENT

The visualization should clearly show:

- recommendation duration
- recommendation transitions
- recommendation frequency
- periods of market stability
- periods of market volatility

---

# 3. Recommendation Change Log

The Change Log records only meaningful recommendation transitions.

If the recommendation remains unchanged, no entry is generated.

Each recommendation change records:

- Timestamp
- Previous Recommendation
- New Recommendation
- Previous Market State
- New Market State
- Confidence Change
- Opportunity Score Change
- FVR Change
- Expected ROI Change
- Primary Decision Driver

Example

```
2026-07-21 14:00 UTC

DO NOT RENT → WATCH

Confidence

52 → 67

Opportunity Score

48 → 63

Fair Value Ratio

0.79 → 0.86

Expected ROI

-14.2% → -4.1%

Primary Reason

Rental premium decreased while BCH price increased.
```

---

# 4. Decision Metric Trends

Historical charts visualize the engine's decision metrics over time.

Initial charts should include:

- Confidence
- Opportunity Score
- Fair Value Ratio
- Rental Premium
- Risk-Adjusted ROI
- Probability of Success
- BCH Price
- Network Difficulty

All charts should share a synchronized time axis.

Recommendation transitions should be highlighted on each chart.

---

# 5. Historical Run Details

The Historical Run Details section contains the complete execution history.

Suggested columns:

- Timestamp
- Recommendation
- Market State
- Confidence
- Opportunity Score
- Budget
- Hashrate
- Duration
- Probability
- Expected ROI
- Expected Profit
- Fair Value Ratio
- Rental Premium
- Recommended Pool

Supported functionality:

- Date filtering
- Recommendation filtering
- Market State filtering
- Sorting
- CSV Export

---

# Default Time Range

The default dashboard range should be the previous 30 days.

Available ranges:

- 24 Hours
- 3 Days
- 7 Days
- 30 Days
- 90 Days
- All History

The selected range should apply consistently across:

- Summary metrics
- Recommendation Timeline
- Recommendation Change Log
- Decision Metric Trends
- Historical Run Details

---

# Future Enhancements

The Recommendation History system is designed to support future analytical capabilities without requiring schema changes.

Potential future enhancements include:

- Recommendation Stability Index
- Recommendation Accuracy Analysis
- Decision Driver Frequency
- Recommendation Heatmaps
- Historical Replay Mode
- Strategy Backtesting
- Machine Learning Feature Generation
- Recommendation Forecasting
- Notification History
- Multi-Coin Recommendation Comparison