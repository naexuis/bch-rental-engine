# Developer Journal

The Developer Journal is a chronological record of the development of the BCH Solo Rental Strike Engine.

Unlike the changelog, which records software changes, or the Decision Log, which records architectural decisions, this journal captures the thought process behind the project.

It documents:

- Development milestones
- Lessons learned
- Design ideas
- Technical discoveries
- Mistakes
- Future improvements

The goal is to preserve the project's history so future development has context.

---

# June 2026

## Project Begins

The original goal of this project was simple.

Determine whether Bitcoin Cash solo mining rental opportunities could be evaluated mathematically before renting hashpower.

At the beginning, most decisions were made manually.

Questions included:

- Is BCH expensive?
- Is rental hashpower cheap?
- What is the probability of finding a block?
- What would the expected profit be?

The project started as a collection of Python calculations and quickly grew beyond that.

---

## First Optimization Engine

The first optimization engine evaluated rental opportunities using

- budget
- hashrate
- rental duration

and calculated

- expected blocks
- expected revenue
- ROI

This proved that optimization was possible.

However, it also became clear that ROI alone was not enough.

Probability had to become part of the recommendation.

---

## Risk-Adjusted ROI

One of the first major lessons learned was that expected value can be misleading.

Two rentals might have identical expected profit but vastly different probabilities of success.

This led to the introduction of Risk-Adjusted ROI.

This remains one of the project's most important metrics.

---

# Pool Support

Initially the engine only supported Braiins.

Support was later expanded to MiningRigRentals.

The architecture intentionally abstracts rental providers into adapters so additional marketplaces can be added with minimal changes.

Long-term, the goal is for the optimization engine to remain independent of any specific provider.

---

# Opportunity Score

As the project evolved, it became increasingly difficult to communicate recommendations using a single metric.

ROI alone was insufficient.

Probability alone was insufficient.

Fair Value Ratio alone was insufficient.

The Opportunity Score was created to summarize several important indicators into a single value.

Although imperfect, it provides an intuitive summary for users while preserving access to the underlying metrics.

---

# Historical Database

Initially only the latest recommendation was saved.

It quickly became apparent that historical recommendations would be valuable for understanding trends and validating future improvements.

SQLite was selected because it provides:

- zero administration
- excellent performance
- a single portable file

This decision has greatly simplified development.

---

# Dashboard

The first dashboard was intentionally minimal.

It simply displayed the latest recommendation.

Over time it evolved into an operational dashboard with:

- Decision Center
- Market Overview
- Strike Analysis
- Pool Routing
- Historical Performance
- Candlestick Charts

The guiding philosophy has remained the same:

The dashboard should visualize—not compute.

---

# Candlestick Charts

Adding BCH candlestick charts represented a shift in the dashboard.

Until this point, every visualization was generated solely from engine output.

Candlestick charts introduced external market context.

This allows users to compare the engine's recommendation with recent BCH price movement.

This was also the first major use of Plotly for interactive financial charts.

---

# Log Rotation

One unexpected operational issue was log growth.

JSONL logs continued to grow indefinitely.

Although this was not immediately problematic, it became obvious that unattended servers would eventually accumulate unnecessarily large log files.

Automatic rotation was implemented to ensure predictable disk usage.

This reinforced an important lesson:

Operational features become increasingly valuable as software matures.

---

# Documentation

As the project grew, it became increasingly difficult to remember:

- deployment steps
- configuration details
- architectural decisions

A dedicated documentation effort began to address this.

The goal is for a new developer—or even the future version of the original developer—to understand the project without relying on memory.

Documentation is now considered a core part of development rather than an afterthought.

---

# Lessons Learned

Several themes have emerged during development.

## Keep the architecture simple.

Simple systems are easier to understand, test, and maintain.

---

## Separate responsibilities.

The engine computes.

The dashboard visualizes.

SQLite stores history.

JSON communicates state.

Each component should have a single responsibility.

---

## Configuration is better than hardcoding.

Nearly every parameter eventually benefits from becoming configurable.

---

## Record history.

Historical data has repeatedly proven valuable for:

- debugging
- visualization
- validation
- future research

---

## Explain recommendations.

The best recommendation is not simply:

```
RENT
```

Instead, the system should explain:

- why
- how
- under what assumptions

This philosophy guides nearly every new feature.

---

# Future Ideas

Some ideas currently under consideration include:

- Technical Analysis Engine
- Historical strategy backtesting
- Dashboard settings editor
- Automatic rental execution
- Multi-coin support
- Machine learning recommendations
- Cloud deployment automation
- REST API
- Mobile dashboard
- Alert customization
- Portfolio management

Not every idea will necessarily be implemented, but recording them here preserves them for future consideration.

---

# Personal Notes

One recurring lesson throughout this project is that software development is iterative.

Very few features have been built exactly as originally envisioned.

Most have evolved through repeated refinement.

Several of the project's strongest features—including the Opportunity Score, Pool Routing, Historical Dashboard, and Decision Center—were not part of the original design.

They emerged naturally as the project matured.

This reinforces the importance of remaining flexible while maintaining a consistent architectural philosophy.

---

# Philosophy

The ultimate objective of this project is not merely to predict profitable rentals.

It is to build a transparent, explainable decision-support platform that helps users make informed mining decisions.

Every feature should improve one or more of the following:

- Understanding
- Explainability
- Reliability
- Maintainability
- Portability

If a proposed feature does not improve one of these areas, it should be carefully reconsidered.

---

# Looking Ahead

The BCH Solo Rental Strike Engine has grown from a small experimental script into a modular analytics platform.

Future development will continue to focus on:

- Better decision intelligence
- Better visualizations
- Better historical analysis
- Better operational tooling
- Better documentation

The architecture has been intentionally designed so these improvements can be added incrementally without requiring major redesigns.

---

# Final Reflection

One of the goals of this journal is to leave behind more than code.

Code explains *how* a system works.

Documentation explains *what* it does.

This journal explains *why* it became what it is.

If this project is revisited years from now, the hope is that these notes will provide enough context to understand not only the technical implementation, but also the reasoning, trade-offs, and lessons that shaped its evolution.