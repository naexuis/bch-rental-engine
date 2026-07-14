# Project Roadmap

The BCH Solo Rental Strike Engine is an actively evolving decision-support platform for evaluating Bitcoin Cash solo mining opportunities.

This roadmap outlines the planned direction of the project over the coming releases.

The roadmap is divided into major milestones rather than strict release dates.

Features may move between milestones as priorities evolve.

---

# Current Version

**Version:** v1.1.0

**Status:** Active Development

---

# Project Vision

The long-term vision is to create the most comprehensive open-source decision-support platform for cryptocurrency hashpower rentals.

The platform should answer one simple question:

> **"Should I rent hashpower right now?"**

To answer that question, the engine combines:

- Market pricing
- Network conditions
- Rental pricing
- Statistical probability
- Risk analysis
- Historical trends
- Technical analysis
- Operational intelligence

The goal is not to automate decision-making, but to provide transparent, explainable recommendations.

---

# Development Phases

## Phase 1 — Core Engine ✅

Status: Complete

### Completed

- BCH market data
- BCH difficulty tracking
- Network hashrate estimation
- Braiins support
- MiningRigRentals support
- Budget optimization
- Hashrate optimization
- Strike scoring
- Opportunity scoring
- Market regime classification
- Pool routing engine
- Telegram alerts
- SQLite history
- JSON state output
- Streamlit dashboard
- Docker deployment
- Candlestick charts
- Automatic JSONL log rotation
- Comprehensive documentation

---

# Phase 2 — Decision Intelligence 🚧

Status: In Progress

Goal:

Improve recommendation quality through additional analytics.

### Planned

- Technical indicators
- Moving averages
- RSI
- MACD
- Bollinger Bands
- VWAP
- ATR
- Trend strength analysis
- Momentum scoring
- Volatility scoring

Dashboard additions

- Indicator overlays
- Technical summary
- Bull/Bear market gauge

---

# Phase 3 — Historical Analytics

Status: Planned

Goal:

Learn from previous market conditions.

Features

- Historical Opportunity Score charts
- Historical recommendation analysis
- Profitability timeline
- Win/Loss statistics
- Historical FVR distribution
- Historical ROI distribution
- Historical probability analysis

New dashboard pages

- Analytics
- Performance
- Trends

---

# Phase 4 — Strategy Backtesting

Status: Planned

Goal:

Evaluate how historical strategies would have performed.

Features

- Replay historical markets
- Simulate rental decisions
- Historical profit curves
- Historical block probabilities
- Strategy comparison
- Parameter optimization

Possible strategies

- Aggressive
- Conservative
- Probability-first
- ROI-first
- Custom

---

# Phase 5 — Dashboard Enhancements

Status: Planned

Future improvements

### Dashboard Settings

- Editable configuration
- Theme selection
- Refresh interval
- Budget defaults
- Pool preferences

### Better Visualizations

- Heatmaps
- Gauge charts
- Opportunity timeline
- Animated market replay
- Correlation charts

### Better UX

- Mobile layout
- Dark mode improvements
- Keyboard shortcuts
- Faster page loading

---

# Phase 6 — Automation

Status: Planned

Goal

Reduce manual operation.

Features

- Automatic engine scheduling
- Automatic Docker updates
- Automatic Git updates
- Scheduled backups
- Health monitoring
- Email alerts
- SMS alerts
- Discord alerts
- Slack integration

---

# Phase 7 — Cloud Deployment

Status: Planned

Deployment targets

- AWS EC2
- DigitalOcean
- Azure
- Google Cloud
- Linode
- Vultr

Deployment improvements

- Docker Compose
- Nginx
- HTTPS
- Let's Encrypt
- CloudWatch
- Terraform

---

# Phase 8 — Advanced Mining Intelligence

Status: Planned

Features

- Difficulty forecasting
- Hashrate forecasting
- BCH price forecasting
- Rental price forecasting
- Block timing estimation
- Pool congestion prediction
- Rental availability prediction

---

# Phase 9 — Multi-Coin Support

Status: Planned

Potential coins

- Bitcoin
- Litecoin
- Dogecoin
- Kaspa
- Monero

Goal

Create a generalized hashpower rental analysis platform.

---

# Phase 10 — AI Decision Assistant

Status: Long-Term Vision

Features

- Natural language explanations
- Recommendation summaries
- "Why not rent?"
- "What changed?"
- Daily market brief
- Interactive chat assistant
- Personalized recommendations

Example

```
Market conditions improved by 8%.

The recommendation remains WATCH because:

• Probability is still below target.
• Rental prices remain above fair value.
• Opportunity Score increased from 49 to 54.
```

---

# Future Dashboard Pages

Potential additions

- Portfolio
- Alerts
- Backtesting
- Technical Analysis
- Market Health
- Strategy Comparison
- Settings
- API Explorer
- Reports
- Diagnostics

---

# Planned APIs

Possible future REST endpoints

```
GET /recommendation

GET /history

GET /market

GET /technical

GET /pool-routing

GET /dashboard
```

---

# Long-Term Goals

The project aims to become:

- A complete mining decision-support platform
- Easy to deploy
- Highly portable
- Fully documented
- Explainable
- Extensible
- Cloud-ready

---

# Guiding Principles

Every new feature should improve at least one of the following:

- Accuracy
- Explainability
- Reliability
- Maintainability
- Performance
- Portability
- User Experience

Features that do not improve one of these areas should be carefully evaluated before implementation.

---

# Ideas Backlog

Ideas under consideration

- GPU acceleration
- WebSocket live market feeds
- Automatic parameter tuning
- Risk profile presets
- Historical market replay
- PDF report generation
- CSV exports
- REST API
- GraphQL API
- Multi-user dashboard
- Authentication
- S3 backup support
- Local data caching
- Offline mode
- Plugin architecture

---

# Recently Completed

- ✅ Decision Center redesign
- ✅ Historical dashboard
- ✅ Pool routing analysis
- ✅ Opportunity scoring
- ✅ Candlestick charts
- ✅ Readable market metrics
- ✅ Automatic JSONL log rotation
- ✅ Docker dashboard deployment
- ✅ Comprehensive project documentation

---

# Release Milestones

| Version | Focus | Status |
|----------|-------|--------|
| v1.0 | Core Engine | ✅ Complete |
| v1.1 | Dashboard & Documentation | ✅ Complete |
| v1.2 | Technical Analysis | 🚧 In Progress |
| v1.3 | Historical Analytics | 📋 Planned |
| v1.4 | Strategy Backtesting | 📋 Planned |
| v1.5 | Automation | 📋 Planned |
| v2.0 | AI Decision Platform | 🔮 Vision |

---

# Contributing

Future contributors are encouraged to:

- Keep the architecture modular.
- Prefer configuration over hardcoded values.
- Document architectural decisions.
- Maintain portability across Linux environments.
- Preserve explainability in all recommendation logic.
- Write clear documentation alongside new features.

---

# Success Criteria

The project will be considered successful if it:

- Produces transparent, data-driven rental recommendations.
- Can be deployed on any Linux server in under 30 minutes.
- Maintains a complete historical record of recommendations.
- Remains easy to understand and extend.
- Helps users make better-informed mining decisions.

---

# Looking Ahead

The BCH Solo Rental Strike Engine has evolved from a simple probability calculator into a comprehensive mining analytics platform.

Future development will continue to focus on:

- Smarter recommendations
- Better visualizations
- Stronger operational tooling
- Richer historical analysis
- Simplified deployment
- Expanded market intelligence

The long-term objective is to build a platform that users can trust not because it predicts the future, but because it clearly explains the trade-offs behind every recommendation.