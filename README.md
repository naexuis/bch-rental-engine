# BCH Solo Rental Strike Engine

A self-hosted decision-support system for evaluating short-window Bitcoin Cash solo mining rental opportunities.

The project combines market data, hashpower rental pricing, block probability modeling, risk-adjusted economics, pool routing, historical tracking, Telegram alerts, and a Streamlit dashboard.

## Features

- BCH and BTC market data
- BCH network difficulty and estimated network hashrate
- Braiins and MiningRigRentals hashpower support
- Budget and hashrate range optimization
- Poisson block probability modeling
- Expected revenue, profit, ROI, and risk-adjusted ROI
- Fair Value Ratio calculation
- Market regime classification
- Opportunity scoring
- Pool routing recommendations
- Budget frontier and optimization surface
- SQLite historical database
- JSON state output
- Rotating JSONL operational logs
- Telegram alerts
- Streamlit dashboard
- BCH candlestick charts with multiple time ranges
- Docker deployment support

## Project Status

Current Version: **v1.1.0**

Status: **Active Development**

Completed:

- ✅ BCH rental optimization engine
- ✅ Streamlit dashboard
- ✅ Historical SQLite database
- ✅ Candlestick market analysis
- ✅ Opportunity scoring
- ✅ Pool routing
- ✅ Telegram alerts
- ✅ Docker deployment
- ✅ Automatic log rotation

In Progress:

- 📖 Documentation
- 📈 Technical Analysis Engine

Planned:

- Dashboard configuration editor
- Market health score
- Historical strategy backtesting

## Architecture

```text
Market APIs
    |
    v
BCH Rental Engine
    |
    +--> Latest JSON State
    |
    +--> SQLite History
    |
    +--> Rotating JSONL Logs
    |
    +--> Telegram Alerts
    |
    v
Streamlit Dashboard
```

## Repository Structure

bch-rental-engine/
├── config/
│   ├── .env
│   ├── pools.json
│   └── dashboard_config_override.json
├── dashboard/
│   └── app.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── CONFIGURATION.md
│   ├── DECISION_LOG.md
│   ├── DEPLOY_EC2.md
│   ├── DEVELOPER_JOURNAL.md
│   ├── INSTALL.md
│   ├── OPERATIONS.md
│   └── ROADMAP.md
├── scripts/
│   ├── bch_solo_rental_strike_engine.py
│   └── pools/
├── Dockerfile
├── Dockerfile.dashboard
├── requirements.txt
├── run_engine.sh
└── README.md

## Quick Start

1. Clone the repository

```
git clone https://github.com/naexuis/bch-rental-engine.git
cd bch-rental-engine
```

2. Create a virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies

```
pip install --upgrade pip
pip install -r requirements.txt
```

4. Create the configuration file

Create

```
config/.env
```

At a minimum, configure one hashpower source, for example:

```
BRAIINS_BTC_PER_EH_DAY=0.50049
BRAIINS_AVAILABLE_PH=300
```

5. Run the engine

```
set -a
source config/.env
set +a

python scripts/bch_solo_rental_strike_engine.py
```

6. Run the dashboard

```
streamlit run dashboard/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0
```

Then open the dashboard at the following address

```
http://SERVER_IP:8501
```

## Docker

1. Build the engine:

```
docker build -t bch-rental-engine .
```

2. Build the dashboard

```
docker build \
  -f Dockerfile.dashboard \
  -t bch-rental-dashboard .
```

## Main Outputs

The engine writes:

```
~/bch_rental_engine/state/bch_solo_rental_strike_engine.json
~/bch_rental_engine/state/bch_rental_history.sqlite
~/bch_rental_engine/logs/bch_solo_rental_strike_engine.jsonl
~/bch_rental_engine/logs/bch_solo_rental_strike_engine_alerts.jsonl
```

## Safety

This project is a decision-support tool. It does not guarantee mining success or profitability.

Solo mining outcomes are probabilistic, and a rental can lose the entire rental cost if no block is found. Always verify rental pricing, pool configuration, payout details, and execution conditions before spending funds.

## Documentation

[Installation](projects/bch-rental-engine/docs/INSTALL.md)

[Configuration](projects/bch-rental-engine/docs/CONFIGURATION.md)

[Architecture](projects/bch-rental-engine/docs/ARCHITECTURE.md)

[Operations](projects/bch-rental-engine/docs/OPERATIONS.md)

[Deploy to EC2](projects/bch-rental-engine/docs/DEPLOY_EC2.md)

[Roadmap](projects/bch-rental-engine/docs/ROADMAP.md)

[Changelog](projects/bch-rental-engine/docs/CHANGELOG.md)

[Developer Journal](projects/bch-rental-engine/docs/DEVELOPER_JOURNAL.md)

[Decision Log](projects/bch-rental-engine/docs/DECISION_LOG.md)

## Current Status

The project currently supports monitoring, strike evaluation, historical analytics, pool routing, dashboard visualization, Telegram alerts, and Docker-based deployment.

Future work includes technical analysis, market health scoring, backtesting, and improved deployment automation.