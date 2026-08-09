# BCH Rental Engine Developer Journal

The Developer Journal is a chronological and reflective record of the BCH Rental Engine’s development.

Unlike the CHANGELOG, which records completed software changes, or the Decision Log, which records formal architectural decisions, this journal captures the reasoning behind the project.

It documents:

* Development milestones
* Design evolution
* Technical discoveries
* Lessons learned
* Mistakes and corrections
* Operational improvements
* Future development ideas

The purpose of this journal is to preserve context.

Code shows how the system works.

Documentation explains what the system does.

This journal records why the system evolved in the way that it did.

⸻

June 2026

Project Begins

The original goal of the BCH Rental Engine was straightforward:

Determine whether Bitcoin Cash solo-mining rental opportunities could be evaluated mathematically before spending money on rented hashpower.

At the beginning, most decisions were made manually.

The key questions were:

* What is the current BCH block reward worth?
* How expensive is rental hashpower?
* What is the probability of finding at least one block?
* How many blocks should be expected statistically?
* What would the expected profit or loss be?
* Is the rental price reasonable relative to fair value?

The project began as a collection of Python calculations.

It quickly became clear that the problem required more than a single calculator.

A useful system would need to combine market data, probability, economics, risk, historical context, and explainable recommendations.

⸻

First Optimization Engine

The first optimization engine evaluated rental scenarios using:

* Budget
* Hashrate
* Rental duration

For each scenario, it calculated:

* Expected blocks
* Probability of finding one or more blocks
* Expected revenue
* Expected profit
* Expected ROI

This proved that rental opportunities could be evaluated systematically.

It also revealed a major limitation:

Expected ROI alone could not represent the real risk of solo mining.

A rental could have an acceptable expected value while still carrying a high probability of returning nothing.

This became one of the earliest and most important design lessons.

⸻

Probability Becomes a Core Metric

Solo mining outcomes are highly variable.

A positive expected return does not guarantee a profitable result, and a negative expected return does not make a successful block impossible.

The engine therefore began treating probability as a first-class decision metric.

Probability calculations were expanded to include:

* Expected number of blocks
* Probability of finding at least one block
* Probability of finding multiple blocks
* Probability targets by budget and hashrate
* Probability-aware scenario ranking

This shifted the system away from simple profitability analysis and toward risk-aware decision support.

⸻

Risk-Adjusted ROI

One of the earliest major lessons was that expected value can be misleading when viewed without probability.

Two rentals can have similar expected profit but very different chances of producing a successful outcome.

Risk-Adjusted ROI was introduced to reflect this distinction.

The metric was intended to help balance:

* Expected profitability
* Probability of success
* Capital at risk
* Rental duration
* Outcome uncertainty

Risk-Adjusted ROI remains one of the engine’s most important decision metrics.

It also reinforced a broader principle:

No single metric should determine the recommendation.

⸻

Fair Value Ratio

Rental price needed to be evaluated relative to the underlying economic value of the hashpower.

This led to the Fair Value Ratio.

The Fair Value Ratio compares the economic value of expected mining output with the price of the rental.

It helps answer:

* Is the rental priced below fair value?
* Is the rental priced near fair value?
* Is the rental carrying a significant premium?
* How much would pricing need to improve before the opportunity became attractive?

The Fair Value Ratio became an important input to:

* Market regime classification
* Opportunity scoring
* Recommendation blockers
* Interpretation text
* Trend analysis

⸻

Hashpower Provider Support

Initial Provider Integration

The engine initially relied heavily on Braiins pricing information.

The first provider integration allowed the engine to evaluate current rental economics using a live or manually configured BTC-per-EH-per-day value.

This was useful, but it also exposed the risks of depending on a single source.

⸻

MiningRigRentals Integration

Support was expanded to MiningRigRentals.

This required the engine to account for:

* Available rigs
* Different hashrates
* Minimum rental durations
* Maximum rental durations
* Provider-specific pricing
* Long-duration rental rules
* API availability
* Raw-response preservation for debugging

MiningRigRentals also introduced practical constraints that were not obvious in the original mathematical model.

For example, the theoretically optimal rental duration may not be available in the marketplace.

The engine therefore had to distinguish between:

* Mathematically ideal scenarios
* Operationally available scenarios

⸻

Provider Abstraction

The provider architecture evolved toward adapters and pool-specific modules.

The objective is to keep the optimization and recommendation logic independent of any particular marketplace or pool.

The provider layer should be responsible for:

* Retrieving provider data
* Normalizing pricing
* Reporting availability
* Handling provider-specific errors
* Returning a consistent internal representation

The decision engine should not need to know how each provider retrieves its data.

This principle will make future integrations easier.

⸻

Pool Routing

As the engine became more operational, selecting a rental scenario was no longer sufficient.

The engine also needed to recommend where the rented hashrate should be directed.

Pool-routing support was introduced to evaluate mining pools using consistent criteria.

Pool adapters were separated into reusable modules under:

scripts/pools/

The pool-routing architecture supports:

* Provider-specific status checks
* Fee comparison
* Reliability considerations
* Pool scoring
* Recommended-pool selection
* Future pool expansion

The long-term goal is for pool routing to remain independent of the opportunity-scoring system while still contributing to the final recommendation.

⸻

Opportunity Score

As the engine evolved, communicating recommendations through several separate metrics became increasingly difficult.

ROI alone was insufficient.

Probability alone was insufficient.

Fair Value Ratio alone was insufficient.

Rental premium alone was insufficient.

The Opportunity Score was created as a summary measure that combines the most important economic and probabilistic indicators into a value from 0 to 100.

The Opportunity Score is not intended to replace the underlying metrics.

Instead, it provides an intuitive summary while preserving access to:

* Probability
* Fair Value Ratio
* Expected profit
* Risk-Adjusted ROI
* Market regime
* Rental premium
* Economic constraints

⸻

Opportunity Actions

A numerical score alone did not provide enough operational meaning.

Opportunity Actions were introduced to convert the score into an internal qualitative assessment.

Current actions include:

* STRIKE_NOW
* STRONG_WATCH
* WATCH
* WEAK_WATCH
* WAIT

These actions represent the engine’s internal view of the opportunity.

They are more granular than the simplified operator recommendation shown on the dashboard.

⸻

Economic Score Caps

An important scoring lesson emerged during calibration:

A high score should not be possible when the underlying economics are clearly unattractive.

Economic score caps were introduced to prevent secondary metrics from overpowering major financial blockers.

Examples include:

* Fair Value Ratio materially below acceptable levels
* Negative expected profitability
* Excessive rental premium
* Weak risk-adjusted returns

This change improved the integrity of the Opportunity Score.

It also reinforced the principle that scoring systems should be calibrated using realistic counterexamples, not only ideal scenarios.

⸻

Characterization Tests

Before changing the Opportunity Score behavior, characterization tests were added to document existing behavior.

This was an important engineering step.

The tests created a stable reference point and made it possible to refine the scoring system without unintentionally changing unrelated outcomes.

Characterization testing became part of the broader testing philosophy of the project.

⸻

Recommendation Hierarchy

The engine’s decision pipeline evolved into several layers.

Opportunity Score

A numerical measure of opportunity attractiveness.

Opportunity Action

The engine’s internal qualitative interpretation.

Alert Tier

A notification-oriented severity classification.

Operator Recommendation

The simplified instruction shown to the operator.

Typical operator recommendations include:

* RENT
* NEAR STRIKE
* WATCH
* DO NOT RENT

This layered design allows the system to preserve analytical detail while presenting a simple final recommendation.

⸻

Explainability

As the recommendation system became more sophisticated, it became increasingly important to explain the output.

A recommendation such as:

DO NOT RENT

is not sufficient on its own.

The operator also needs to understand:

* Why the recommendation was produced
* Which factors are blocking a rental
* Which conditions are improving
* What would need to change
* Whether the opportunity is moving closer to a strike

Explainability features were added to produce:

* Market blockers
* Score limiters
* Conditions required to rent
* Recommendation reasoning
* Opportunity interpretation
* Comparison with the previous execution

This became one of the project’s defining philosophies:

The engine should not merely classify an opportunity.

It should explain the decision.

⸻

Recommendation History

From Latest State to Historical Intelligence

The earliest versions of the engine only preserved the most recent recommendation.

This quickly became limiting.

Without history, the operator could not determine:

* Whether the score was improving
* How long the recommendation had remained unchanged
* Whether market conditions were stable
* Why a recommendation changed
* How often actionable opportunities occurred

SQLite was selected as the historical storage layer because it provides:

* Zero administration
* Strong local performance
* A portable single-file database
* Reliable persistence
* Easy querying
* Straightforward backups

⸻

Snapshot Architecture

Every engine execution now creates a historical Snapshot.

A Snapshot records the engine’s state at a specific point in time.

This includes:

* Timestamp
* Decision pipeline
* Market conditions
* Strike recommendation
* Opportunity Score
* Expected economics
* Pool recommendation
* Engine metadata

The system records every execution, not only recommendation changes.

This makes the database suitable for:

* Trend analysis
* Time-series charts
* Historical replay
* Strategy backtesting
* Future machine learning

⸻

Dynamic Events

Meaningful Events are derived by comparing adjacent Snapshots.

Examples include:

* Operator recommendation changed
* Opportunity Action changed
* Market regime changed
* Opportunity Score crossed a threshold
* Fair Value Ratio improved materially
* Recommended pool changed

Events are derived rather than stored separately.

This avoids duplicated state and ensures that the event logic can evolve without rewriting historical records.

⸻

Generic History Retrieval

The history layer was expanded beyond one fixed query.

Generic history retrieval allows the analytics subsystem to request historical values for different metrics.

This created the foundation for reusable analytics.

Instead of building separate history logic for every metric, the engine can retrieve a numeric series and pass it through a common analytical pipeline.

⸻

Dashboard Evolution

Initial Dashboard

The first dashboard was intentionally minimal.

It displayed the latest recommendation and a small number of supporting metrics.

This was sufficient for early experimentation but not for ongoing operation.

⸻

Operator Console

The dashboard evolved into a broader operator console containing:

* Decision Center
* Market Overview
* Strike Analysis
* Pool Routing
* Historical Performance
* Candlestick Charts
* Recommendation History
* Interpretation text

The dashboard’s guiding philosophy remains:

The engine computes.

The dashboard visualizes.

The dashboard should not reproduce business logic that belongs in the engine.

⸻

Candlestick Charts

Adding BCH candlestick charts introduced external market context into the dashboard.

Previously, most visualizations were generated entirely from engine output.

Candlestick charts allow the operator to compare:

* BCH price movement
* Recent volatility
* Market direction
* Recommendation timing

This was also an early major use of interactive Plotly financial visualizations.

⸻

Recommendation History Dashboard

The Recommendation History page was designed to emphasize decision evolution rather than raw database rows.

The dashboard should help answer:

* What is the engine recommending now?
* Has the recommendation changed?
* Is the opportunity improving or deteriorating?
* How strong is the current trend?
* How frequently do actionable signals occur?

Planned and current visual components include:

* Recommendation timelines
* Opportunity Action timelines
* Change logs
* Opportunity Score charts
* Historical metric charts
* Detailed run tables
* Exportable history

⸻

Trend Intelligence

Why Trend Analysis Was Needed

A single Opportunity Score only describes the current state.

It does not explain whether the opportunity is:

* Improving
* Declining
* Stable
* Accelerating
* Losing momentum

Recommendation History made it possible to analyze how metrics evolve over time.

Trend Intelligence was created as a reusable analytics subsystem rather than a one-off Opportunity Score feature.

⸻

Generic Numeric Trend Engine

The numeric trend engine accepts a historical numeric series and determines:

* Current value
* Previous value
* Latest change
* Direction
* History depth

The implementation was designed to remain generic so that the same logic can later analyze:

* Opportunity Score
* Fair Value Ratio
* Expected ROI
* Rental premium
* BCH price
* Difficulty
* Network hashrate

⸻

Generic Metric Trend Engine

A metric-level wrapper connects history retrieval to numeric analysis.

The architecture now follows:

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

This separation keeps database access, numerical analysis, and presentation independent.

⸻

Trend Direction

Current direction classifications include:

* IMPROVING
* DECLINING
* STABLE
* UNKNOWN, when history is insufficient

Direction provides the simplest interpretation of historical movement.

However, direction alone does not indicate whether a trend is reliable.

This led to the next layers of trend analysis.

⸻

Trend Confidence

Trend confidence was added to estimate how much trust should be placed in the observed direction.

Confidence considers factors such as:

* Number of observations
* Consistency of movement
* Available history
* Directional agreement

Current confidence levels include:

* HIGH
* MEDIUM
* LOW
* UNKNOWN, where appropriate

The purpose of confidence is not to predict the future.

It communicates the quality of the historical evidence behind the current trend.

⸻

Trend Persistence

Persistence measures how many consecutive observations have moved in the same direction.

Examples include:

* One improvement
* Three consecutive improvements
* Seven consecutive declines

Persistence helps distinguish between:

* A single isolated movement
* A sustained directional trend

This provides important context for both confidence and trend strength.

⸻

Trend Velocity

Velocity measures the rate at which a metric is changing.

A trend can be persistent but slow.

Another trend can be shorter but moving rapidly.

Velocity was added to distinguish these cases.

The current implementation flows through:

calculate_numeric_trend
        │
        ▼
calculate_metric_trend
        │
        ▼
analyze_metric
        │
        ▼
calculate_trend_strength

Velocity is now included in trend-strength decision logic.

A medium-confidence, low-volatility, persistent trend can be promoted from MODERATE to STRONG when velocity is sufficiently high.

This was the first use of velocity as an active classification input rather than only a reported metric.

⸻

Trend Volatility

Volatility was added to distinguish stable movement from noisy movement.

A trend with large inconsistent fluctuations should not be interpreted the same way as a smooth sustained trend.

Current volatility classifications include:

* LOW
* HIGH

Volatility contributes to trend-strength classification and helps prevent noisy data from being over-interpreted.

Future work may introduce additional levels or normalized volatility measures.

⸻

Trend Strength

Trend strength combines several analytical dimensions into a single classification.

Current inputs include:

* Direction
* Confidence
* Persistence
* Volatility
* Velocity

Current classifications include:

* VERY_STRONG
* STRONG
* MODERATE
* UNKNOWN

The current logic includes:

* High-confidence, low-volatility, long-persistence trends classified as VERY_STRONG
* High-confidence, low-volatility, sustained trends classified as STRONG
* Medium-confidence, low-volatility, persistent trends classified as MODERATE
* High-velocity promotion from MODERATE to STRONG
* Unsupported or weak combinations classified as UNKNOWN

This is an intentionally conservative framework.

The engine should avoid claiming that a trend is strong without sufficient supporting evidence.

⸻

Interpretation Integration

Trend analytics were integrated into the engine’s interpretation text.

The interpretation system can now explain:

* Current direction
* Confidence
* Persistence
* Velocity
* Volatility
* Trend strength

This allows the operator to see not only the present recommendation but also how the underlying opportunity is evolving.

Interpretation remains a presentation layer.

It should describe analytical results without recomputing them.

⸻

Test-Driven Development

TDD Becomes the Standard Workflow

As the engine grew, small changes began carrying greater regression risk.

A strict Test-Driven Development workflow was adopted.

The current development cycle is:

Write one failing test
↓
Compile
↓
Run the targeted test file
↓
Make the smallest production change
↓
Compile
↓
Run the targeted test file
↓
Commit
↓
Repeat

This workflow prevents unrelated changes from being bundled together.

It also makes failures easier to understand.

⸻

Targeted Test Suites

Features are developed and verified through focused test modules.

Current test coverage includes areas such as:

* Opportunity Score
* Recommendation History
* Numeric trends
* Metric trends
* Confidence
* Persistence
* Velocity
* Volatility
* Trend strength
* Interpretation behavior

Targeted tests are run during each TDD cycle.

The full regression suite should be run before deployment or release.

⸻

Small Commits

Each logical change is committed separately.

Recent trend work followed this pattern:

* Add trend classification behavior
* Add velocity input
* Add a failing velocity-promotion test
* Implement the smallest promotion rule
* Verify all trend tests
* Commit the isolated change

This creates a readable Git history and makes regressions easier to trace.

⸻

Development and Production Separation

A clear separation now exists between development and production.

Development Environment

Typical location:

~/projects/bch-rental-engine

Used for:

* Coding
* Tests
* Documentation
* Experimental work
* Feature commits

⸻

Production Environment

Typical Umbrel location:

~/bch_rental_engine

Used for:

* Stable engine execution
* Streamlit dashboard
* Recommendation History
* Operational state
* Docker deployment

The production working tree should remain clean.

Development commits should not be pulled into production until the feature is complete, regression-tested, documented, pushed, and intentionally released.

This separation has become an important operational safeguard.

⸻

Docker and Umbrel Operations

The production Streamlit dashboard is deployed through Docker.

The repository now contains operational helper scripts for:

* Building the dashboard
* Deploying the dashboard
* Restarting the dashboard
* Checking dashboard health
* Updating production
* Displaying the deployed version
* Backing up state

The preferred production update workflow is:

cd ~/bch_rental_engine
./scripts/update_dashboard.sh

The update process verifies the Git state, fetches changes, builds the image, replaces the container, and performs a health check.

Manual Docker commands are now considered troubleshooting tools rather than the normal deployment method.

⸻

Operational Maturity

Log Rotation

JSONL logs originally grew indefinitely.

Automatic log rotation was added to provide predictable disk usage.

This reinforced an important lesson:

Operational features become more important as software becomes persistent and unattended.

⸻

Backups

The SQLite Recommendation History database is now one of the project’s most valuable assets.

Backup support was added for:

* State
* Configuration
* Logs

The most important file is:

state/bch_rental_history.sqlite

Preserving this database protects the historical intelligence used for trends, replay, and future model validation.

⸻

Health Checks

Dashboard health-check tooling was added to make deployments more reliable.

A successful deployment now requires more than a running Docker container.

The application must also become accessible and pass its health check.

This represents a shift from manual operation toward repeatable production administration.

⸻

Documentation Expansion

As the engine matured, documentation became necessary to preserve operational and architectural knowledge.

The documentation set now includes:

* Architecture
* Configuration
* Installation
* Operations
* Deployment
* Recommendation History
* Release Checklist
* Roadmap
* Decision Log
* Developer Journal
* Changelog

Documentation is treated as part of the implementation.

A feature is not fully complete until the relevant documentation reflects the new behavior.

⸻

Lessons Learned

Keep the architecture simple

The strongest architectural decisions have generally been the simplest.

Examples include:

* SQLite for history
* JSON for current state
* JSONL for operational logs
* Streamlit for visualization
* Docker for dashboard deployment

Simple systems are easier to understand, test, maintain, and recover.

⸻

Separate responsibilities

The engine computes.

The database stores history.

The analytics layer interprets history.

The dashboard visualizes.

The deployment scripts operate production.

Each component should have a clearly defined responsibility.

⸻

Prefer generic analytical functions

The trend subsystem became more useful when it was designed around generic numeric metrics rather than Opportunity Score alone.

Reusable functions reduce duplication and make future analytics easier to add.

⸻

Configuration is better than hardcoding

Nearly every threshold, path, duration, budget, provider setting, and operational limit eventually benefits from configuration.

Hardcoded assumptions should be limited to stable structural rules.

⸻

Preserve history early

Historical data becomes more valuable over time.

It supports:

* Debugging
* Validation
* Visualization
* Trend analysis
* Backtesting
* Forecasting
* Future model training

History cannot be recreated retroactively if it was never stored.

⸻

Explain every recommendation

A recommendation without reasoning has limited operational value.

The system should explain:

* What happened
* Why it matters
* What is blocking action
* What would improve the recommendation
* Which direction conditions are moving

Explainability should remain a core design requirement.

⸻

Add one behavior at a time

Bundling several analytical rules into one change makes failures difficult to diagnose.

The strict TDD process has shown that small behavioral increments are safer and easier to validate.

⸻

Production should remain boring

Production should be stable, clean, predictable, and intentionally updated.

Experimental work belongs in development.

The ideal production deployment should involve a tested release and a repeatable update script, not manual source-code edits.

⸻

Current State

The BCH Rental Engine has evolved from a probability calculator into a layered decision-support platform.

Current major capabilities include:

* Live BCH and BTC market data
* Network difficulty and hashrate analysis
* Hashpower rental evaluation
* Scenario optimization
* Probability analysis
* Risk-Adjusted ROI
* Fair Value Ratio
* Market regime classification
* Opportunity Score
* Opportunity Actions
* Alert tiers
* Operator recommendations
* Pool routing
* Telegram alerts
* JSON state output
* Rotating JSONL logs
* SQLite Recommendation History
* Generic history retrieval
* Explainable recommendation logic
* Trend direction
* Trend confidence
* Trend persistence
* Trend velocity
* Trend volatility
* Trend strength
* High-velocity trend promotion
* Trend interpretation
* Streamlit dashboard
* Dockerized Umbrel deployment
* Operational helper scripts
* Test-driven development workflow

⸻

Active Development Direction

The next major development area is Forecast Intelligence.

Trend Intelligence explains what has happened and how conditions are currently moving.

Forecast Intelligence will attempt to identify how that movement is changing.

The objective is not to claim certainty about future market conditions.

The goal is to provide earlier, better-qualified signals.

⸻

Planned Forecast Intelligence

Trend Acceleration

Determine whether improvement or decline is becoming faster over time.

This may help distinguish:

* Gradual improvement
* Rapidly strengthening opportunities
* Deteriorating economics
* Sudden market changes

⸻

Trend Deceleration

Detect when a trend remains directional but is losing momentum.

This may provide early warning that an improving opportunity is beginning to plateau.

⸻

Trend Reversal Detection

Identify transitions such as:

* Improving to declining
* Declining to improving
* Improving to stable
* Declining to stable

Reversal detection should require sufficient evidence to avoid reacting to isolated noise.

⸻

Plateau Detection

Identify periods where a metric remains within a narrow range.

Plateaus may indicate:

* Market equilibrium
* Limited immediate opportunity
* A pending breakout
* Insufficient movement for a meaningful recommendation change

⸻

False-Trend Detection

Identify apparent trends that are caused by:

* One-time spikes
* Outliers
* Insufficient observations
* Alternating movements
* High volatility

False-trend detection should improve operator trust by reducing overconfident classifications.

⸻

Forecast Confidence

Forecasts should include explicit confidence.

The confidence framework may consider:

* Historical depth
* Trend strength
* Acceleration consistency
* Volatility
* Persistence
* Recent reversals
* Forecast horizon

Forecasts should never be displayed without indicating uncertainty.

⸻

Early Strike Opportunity Detection

The long-term objective of Forecast Intelligence is to identify conditions that may be approaching a viable rental opportunity.

Potential signals include:

* Fair Value Ratio improving
* Rental premium declining
* Opportunity Score accelerating
* Risk-Adjusted ROI approaching zero
* Probability improving at the target budget
* Multiple metrics improving simultaneously

The engine should describe these as emerging opportunities rather than guaranteed future strikes.

⸻

Planned Historical Analytics

Recommendation History will support additional analysis, including:

* Recommendation Stability Index
* Opportunity frequency
* Time spent in each recommendation
* Opportunity Action transition rates
* Market regime transition rates
* Historical Opportunity Score distributions
* Fair Value Ratio distributions
* ROI distributions
* Decision-driver analysis
* Trend-strength distributions

These features will help evaluate how the engine behaves over long periods.

⸻

Planned Strategy Backtesting

Backtesting will allow historical market states to be replayed through defined strategies.

Potential capabilities include:

* Replay historical recommendations
* Compare alternative score thresholds
* Compare probability targets
* Evaluate different budget policies
* Measure recommendation frequency
* Simulate strike execution rules
* Compare forecast signals with realized outcomes

Backtesting will require careful distinction between information available at the time and information learned later.

Avoiding look-ahead bias will be essential.

⸻

Planned Dashboard Intelligence

Future dashboard work may include:

* Trend explorer
* Forecast panel
* Recommendation timeline
* Opportunity heat map
* Historical playback
* Multi-metric overlays
* Trend-strength indicators
* Forecast-confidence indicators
* Decision-driver drill-down
* Recommendation stability charts
* Strategy comparison views

The dashboard should continue to visualize engine output rather than duplicate analytical logic.

⸻

Planned Operational Improvements

Potential operational enhancements include:

* Engine heartbeat
* Automated health monitoring
* Resource-usage monitoring
* Failure alerts
* Scheduled reports
* Automated backups
* Backup retention policies
* Systemd integration
* Release-tag deployment
* CI/CD validation
* Blue-green dashboard deployment

These features should be introduced gradually and only when they improve reliability or reduce operational risk.

⸻

Planned Notification Expansion

Current alerts use Telegram.

Future notification channels may include:

* Email
* Discord
* Slack
* SMS

Notification logic should remain separate from analytical logic.

The engine should produce structured alert data, and notification adapters should decide how that information is delivered.

⸻

Longer-Term Ideas

Longer-term possibilities include:

* Multi-coin support
* REST API
* Mobile dashboard
* Portfolio-level rental analysis
* Machine-assisted market summaries
* Daily opportunity brief
* Automated strategy comparison
* Predictive Opportunity Score
* Interactive operator assistant
* Optional automated rental execution

Automatic rental execution would require substantial safeguards and should only be considered after the recommendation system has been validated over a meaningful historical period.

⸻

Personal Reflection

One of the clearest lessons from this project is that software rarely evolves exactly as initially imagined.

The strongest features were not all part of the original design.

Recommendation History emerged from the need to preserve past decisions.

Trend Intelligence emerged from Recommendation History.

Forecast Intelligence is now becoming possible because trend direction, confidence, persistence, velocity, volatility, and strength were implemented first.

This progression demonstrates the value of layered development.

Each subsystem creates the foundation for the next one.

⸻

Development Philosophy

The ultimate objective of the BCH Rental Engine is not to predict profitable rentals perfectly.

The objective is to build a transparent and trustworthy decision-support platform.

Every feature should improve at least one of the following:

* Recommendation quality
* Explainability
* Reliability
* Testability
* Maintainability
* Performance
* Portability
* Operator experience

Features that do not improve one of these areas should be carefully reconsidered.

⸻

Looking Ahead

The BCH Rental Engine has grown from an experimental mining calculator into a modular historical and analytical platform.

Future development will focus on:

* Better-qualified trends
* Earlier opportunity detection
* Forecast confidence
* Historical validation
* Strategy backtesting
* More useful dashboard intelligence
* Stronger production monitoring
* Continued documentation
* Small, test-driven improvements

The architecture has been intentionally designed so that these capabilities can be added incrementally without requiring a major redesign.

⸻

Final Reflection

One purpose of this journal is to leave behind more than source code.

Code explains how a system works.

Technical documentation explains what it does.

Tests describe expected behavior.

Git history records individual changes.

This journal explains why those changes were made and how the project’s philosophy evolved.

If the BCH Rental Engine is revisited years from now, these notes should provide enough context to understand not only the implementation, but also the reasoning, trade-offs, mistakes, and lessons that shaped the platform.

⸻

Version 0.2.0 Production Validation — August 9, 2026

Version 0.2.0 completed the Storage & Reliability milestone and was validated on the production Umbrel installation.

Production validation confirmed:

* The existing SQLite Recommendation History database migrated from schema version 0 to schema version 1.
* All 790 pre-upgrade history rows were preserved.
* New Recommendation History rows continued to be written after migration.
* The final production verification observed 796 history rows.
* SQLite PRAGMA integrity_check returned ok.
* The required Version 0.2 history columns were present after migration.
* The Storage dashboard reported healthy production storage.
* Manual database compaction through the Storage page completed successfully.
* The Settings page successfully persisted dashboard_config_override.json.
* The production history retention override was verified at 1073741824 bytes (1 GiB).
* The engine completed normal post-migration execution.
* The dashboard started successfully without a runtime exception.
* Engine and dashboard containers were running ghcr.io/naexuis/bch-rental-engine:0.2.0.
* The final image resolved to GHCR digest sha256:66937fd74f760bb9edf6a99e0f2a28a9e88822e8bb19d767b9d3ffac6b004c76.
* The final 0.2.0 deployment used the same registry artifact previously validated as the release candidate.

The production migration demonstrated that the Version 0.2 storage architecture could upgrade the existing historical database in place without destroying Recommendation History.

The verified pre-upgrade rollback database remains preserved separately and should not be overwritten or deleted.
