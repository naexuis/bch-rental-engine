# BCH Rental Engine — Recommendation Decision Model

## Purpose

Define one coherent decision model for rental recommendations while preserving the existing scenario, opportunity, history, dashboard, and alert interfaces during migration.

## Current Decision Layers

### 1. Scenario Alert Tier

Produced by `classify_alert_tier()`.

Current values:

- `STRONG_RENT`
- `DEPLOY_NOW`
- `NEAR_STRIKE`
- `WATCH_IMPROVING`
- `DO_NOT_RENT`

Primary inputs:

- Fair Value Ratio
- Risk-adjusted ROI
- Probability of at least one block

### 2. Scenario Recommendation

Produced by `recommendation_from_tier()`.

Current values:

- `RENT`
- `NEAR STRIKE`
- `WATCH`
- `DO NOT RENT`

### 3. Opportunity Score

Produced by `calculate_opportunity_score()`.

Current range:

- `0–100`

Components:

- FVR score: maximum 65 points
- Probability score: maximum 20 points
- ROI score: maximum 15 points

Hard caps prevent poor economics from producing high scores.

### 4. Opportunity Action

Derived from Opportunity Score.

Current values:

- `STRIKE_NOW`
- `STRONG_WATCH`
- `WATCH`
- `WEAK_WATCH`
- `WAIT`

### 5. Dashboard Operator Action

Derived from scenario recommendation.

Current visible values:

- `RENT NOW`
- `RENT`
- `WATCH`
- `MONITOR`
- `WAITING`
- `DO NOT RENT`

The dashboard currently maps `NEAR STRIKE` to `WATCH`.

## Current Problems

1. Multiple decision vocabularies overlap.
2. The scenario recommendation and Opportunity Action can disagree.
3. The dashboard applies another translation layer.
4. Some dashboard mappings represent values the engine does not normally emit.
5. Opportunity Score is labeled as confidence even though it is an attractiveness score.
6. There is no authoritative reconciliation rule.

## Proposed Canonical Decision States

The engine should eventually produce one canonical decision:

- `RENT_NOW` — all hard gates pass with strong economics and high conviction.
- `READY` — all minimum hard gates pass, but conditions do not qualify for `RENT_NOW`.
- `WATCH_CLOSELY` — economics are near the execution threshold.
- `WATCH` — conditions may be improving but are not yet close enough to execute.
- `WAIT` — required data is available, but current economics are unattractive.
- `UNAVAILABLE` — required pricing or market data is missing.

## Proposed Responsibilities

### Canonical Decision

The authoritative operator decision.

### Opportunity Score

A continuous measure of opportunity attractiveness, not confidence.

### Confidence

A separate measure of confidence in the canonical decision.

### Scenario Alert Tier

Retained temporarily for backward compatibility and derived from the canonical decision.

### Scenario Recommendation

Retained temporarily for backward compatibility and derived from the canonical decision.

### Opportunity Action

Retained temporarily for history compatibility and derived from the canonical decision.

## Proposed Hard Gates

A rental decision should require all applicable hard gates:

- Executable pricing source exists.
- Scenario is executable.
- Fair Value Ratio meets the required threshold.
- Risk-adjusted ROI is positive.
- Probability of at least one block meets the required threshold.
- Market and source data pass sanity checks.

## Proposed Soft Inputs

These should affect score, confidence, or explanation but should not independently authorize a rental:

- Trend direction
- Trend strength
- Trend persistence
- Trend acceleration
- Volatility
- Recent Opportunity Score movement
- Market regime

## Initial Compatibility Mapping

| Canonical Decision | Scenario Recommendation | Opportunity Action | Dashboard Action |
|---|---|---|---|
| `RENT_NOW` | `RENT` | `STRIKE_NOW` | `RENT NOW` |
| `READY` | `RENT` | `STRONG_WATCH` | `RENT` |
| `WATCH_CLOSELY` | `NEAR STRIKE` | `WATCH` | `WATCH` |
| `WATCH` | `WATCH` | `WEAK_WATCH` | `WATCH` |
| `WAIT` | `DO NOT RENT` | `WAIT` | `DO NOT RENT` |
| `UNAVAILABLE` | `WAIT` | `WAIT` | `WAITING` |

## Migration Strategy

1. Add a canonical decision model without removing existing fields.
2. Derive legacy outputs from the canonical decision.
3. Add characterization tests for compatibility mappings.
4. Update engine state output.
5. Update dashboard to read the canonical decision.
6. Update alerts and history.
7. Deprecate duplicated decision logic only after compatibility is verified.

## Open Design Questions

1. Should the dashboard display `READY` directly or translate it to `RENT`?
2. Should the minimum P(1+) threshold be fixed or configurable?
3. Should trend information influence the canonical decision or only confidence?
4. Should `WATCH_CLOSELY` require improving trends?
5. Should Opportunity Score thresholds remain fixed?
6. Should the dashboard label Opportunity Score as attractiveness rather than confidence?

## Definition of Done

- One canonical decision exists.
- All legacy outputs are derived from it.
- The dashboard and CLI show the same operator guidance.
- Opportunity Score and confidence are clearly distinguished.
- No contradictory recommendation states appear.
- Existing history remains readable.
- All tests pass.
