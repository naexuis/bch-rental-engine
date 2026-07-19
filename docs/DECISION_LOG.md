# Decision Log

The Decision Log records significant architectural and engineering decisions made throughout the development of the BCH Rental Engine.

Unlike the changelog, which records **what** changed, this document explains **why** those decisions were made.

Each decision includes the rationale, alternatives that were considered, and the expected long-term impact on the project.

---

# Decision Format

Each entry follows the same structure:

- Date
- Decision
- Context
- Alternatives Considered
- Decision
- Consequences

---

# 2026-06-23

## Initial Project Architecture

**Context**

The project began as an experiment to determine whether Bitcoin Cash solo mining opportunities could be evaluated quantitatively using publicly available market data.

**Alternatives Considered**

- Spreadsheet calculations
- Single Python notebook
- Modular Python application

**Decision**

Build the project as a modular Python application with reusable components.

**Reasoning**

The project was expected to grow substantially and eventually support multiple pool providers, dashboards, historical analytics, and automated deployment.

**Consequences**

Positive

- Easier maintenance
- Easier testing
- Easier expansion

Negative

- Slightly higher initial complexity

---

# 2026-06-24

## Use JSON for Current State

**Context**

The dashboard needed a way to read the most recent recommendation without executing the optimization engine itself.

**Alternatives Considered**

- SQLite only
- PostgreSQL
- Redis
- JSON

**Decision**

Store the latest engine output as a JSON document.

**Reasoning**

JSON is:

- Human readable
- Easy to debug
- Fast to write
- Fast to read
- Portable

The dashboard only requires the latest engine state.

**Consequences**

Positive

- Loose coupling
- Easy debugging
- Simple deployment

---

# 2026-06-25

## Use SQLite for Historical Data

**Context**

Historical recommendations needed to be retained for analysis and visualization.

**Alternatives Considered**

- CSV
- JSON
- PostgreSQL
- SQLite

**Decision**

Use SQLite.

**Reasoning**

SQLite provides:

- Zero administration
- Excellent analytical performance
- Single portable file
- No external server

**Consequences**

Positive

- Easy backups
- Excellent portability
- Simple deployment

---

# 2026-06-26

## Separate Engine and Dashboard

**Context**

The optimization engine is computationally intensive, while the dashboard only displays results.

**Alternatives Considered**

Run everything inside Streamlit.

**Decision**

Separate the optimization engine from the dashboard.

**Reasoning**

The dashboard should never perform optimization.

Instead:

```
Engine

↓

JSON

↓

Dashboard
```

This separation allows each component to evolve independently.

**Consequences**

Positive

- Faster dashboard
- Better reliability
- Cleaner architecture

---

# 2026-06-28

## Dockerize the Dashboard

**Context**

The dashboard needed a consistent runtime environment across Umbrel and future cloud deployments.

**Alternatives Considered**

Run Streamlit directly on the host.

**Decision**

Deploy the dashboard in Docker.

**Reasoning**

Docker provides:

- Consistent environments
- Easier upgrades
- Simpler deployment
- Isolation from the host system

**Consequences**

Positive

- Improved portability
- Cleaner upgrades

---

# 2026-06-29

## Umbrel as Initial Deployment Platform

**Context**

A low-power, always-on server was needed for continuous monitoring.

**Alternatives Considered**

- Raspberry Pi
- AWS EC2
- Desktop PC

**Decision**

Use Umbrel.

**Reasoning**

Umbrel provides:

- Docker
- Linux
- Low power consumption
- Always-on operation

The architecture remains cloud portable.

---

# 2026-07-01

## Opportunity Score

**Context**

No single metric adequately captures the attractiveness of a mining opportunity.

**Alternatives Considered**

Use only:

- ROI
- Expected Profit
- Fair Value Ratio

**Decision**

Create a composite Opportunity Score.

**Reasoning**

The score combines:

- Fair Value Ratio
- Risk-adjusted ROI
- Probability
- Market Regime

into one overall indicator.

**Consequences**

Positive

- Easier interpretation
- Better ranking of opportunities

---

# 2026-07-02

## Pool Routing Engine

**Context**

The best rental is not necessarily best when directed to every mining pool.

**Alternatives Considered**

Allow users to manually choose pools.

**Decision**

Automatically rank pools.

**Reasoning**

Routing decisions should consider:

- Pool fee
- Existing hashrate
- Network share
- Routing score

**Consequences**

Positive

- Better recommendations
- Reduced user effort

---

# 2026-07-03

## Historical Dashboard

**Context**

Users needed insight into how recommendations change over time.

**Decision**

Add historical charts backed by SQLite.

**Reasoning**

Historical visualization enables:

- Trend analysis
- Market evolution
- Future backtesting

---

# 2026-07-04

## Candlestick Charts

**Context**

Recommendation quality improves when users can view recent BCH market behavior.

**Decision**

Embed interactive candlestick charts in the dashboard.

**Reasoning**

Visual market context complements quantitative recommendations and allows users to identify recent price trends without leaving the application.

---

# 2026-07-05

## Automatic JSONL Log Rotation

**Context**

Operational logs were growing indefinitely.

**Decision**

Automatically rotate JSONL logs after reaching a configurable size.

**Reasoning**

Log rotation prevents unlimited disk growth while preserving recent history for troubleshooting.

**Consequences**

Positive

- Stable disk usage
- Better long-term operation
- No manual cleanup required

---

# Ongoing Principles

The following principles guide all future architectural decisions.

1. Simplicity over complexity.
2. Separate computation from visualization.
3. Favor portable technologies.
4. Prefer configuration over hardcoded values.
5. Record every recommendation for future analysis.
6. Keep components loosely coupled.
7. Preserve explainability.
8. Avoid unnecessary external services.
9. Design for cloud portability.
10. Build features that can be maintained for years.

---

# Future Decisions

Future entries will document decisions such as:

- Automated rental execution
- Multi-coin support
- Technical Analysis Engine
- AI recommendation assistant
- Cloud-native deployment
- Docker Compose
- Kubernetes support
- Machine learning enhancements

---

# Related Documentation

For additional context, see:

- [Architecture Guide](ARCHITECTURE.md)
- [Operations Runbook](OPERATIONS.md)
- [Developer Journal](DEVELOPER_JOURNAL.md)
- [Changelog](CHANGELOG.md)