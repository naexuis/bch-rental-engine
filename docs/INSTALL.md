BCH Rental Engine Installation Guide

This guide explains how to install the BCH Rental Engine on a new Linux server, Umbrel system, cloud virtual machine, or development workstation.

The BCH Rental Engine includes:

* A Python-based rental opportunity engine
* Live BCH and BTC market data
* Hashpower provider integrations
* Opportunity scoring
* Recommendation logic
* Pool routing
* SQLite Recommendation History
* Trend Intelligence
* JSON and JSONL operational outputs
* Telegram alerts
* A Streamlit operator dashboard
* Docker-based production deployment

The system has been developed primarily on Linux and Umbrel OS using Python 3.13.

Estimated installation time:

20–40 minutes

⸻

1. Supported Environments

The BCH Rental Engine is designed for Linux-based systems.

Operating System	Status
Ubuntu 22.04 LTS	✅ Recommended
Ubuntu 24.04 LTS	✅ Recommended
Umbrel OS	✅ Production tested
Debian 12	✅ Expected to work
Raspberry Pi OS 64-bit	⚠️ Limited testing
macOS	⚠️ Development only
Windows with WSL2	⚠️ Development only

The project assumes:

* Bash shell
* Git
* Python 3.11 or newer
* Internet connectivity
* Docker for production dashboard deployment

Python 3.13 is currently used in the active development environment.

⸻

2. Recommended Environment Model

The recommended architecture separates development from production.

Development Environment

Use the development environment for:

* Feature development
* Test-Driven Development
* Unit testing
* Documentation changes
* Experimental analytics

Example location:

~/projects/bch-rental-engine

⸻

Production Environment

Use the production environment for:

* Scheduled engine execution
* Dashboard hosting
* Recommendation History
* Operator access
* Stable releases

Example Umbrel location:

~/bch_rental_engine

Do not develop directly in the production repository.

Production should remain on a tested and intentionally deployed commit or release tag.

⸻

3. Install System Packages

On Ubuntu or Debian:

sudo apt update
sudo apt install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    sqlite3 \
    curl

Verify the installations:

git --version
python3 --version
sqlite3 --version

Python 3.11 or newer is recommended.

⸻

4. Install Python 3.13 When Required

Some Linux distributions may not provide Python 3.13 by default.

First check the installed version:

python3 --version

When Python 3.13 is already installed:

python3.13 --version

Ensure the virtual-environment package is available:

sudo apt install python3.13-venv

The exact installation method may vary by Linux distribution.

⸻

5. Clone the Repository

Development Installation

Clone into the development directory:

mkdir -p ~/projects
cd ~/projects
git clone https://github.com/naexuis/bch-rental-engine.git
cd bch-rental-engine

⸻

Production Installation

For an Umbrel production installation:

cd ~
git clone https://github.com/naexuis/bch-rental-engine.git \
    bch_rental_engine
cd ~/bch_rental_engine

Verify the repository:

git status
git rev-parse --short HEAD

The working tree should be clean after cloning.

⸻

6. Verify the Repository Structure

The repository should contain files and directories similar to:

Dockerfile
Dockerfile.dashboard
README.md
requirements.txt
run_engine.sh
config/
dashboard/
docs/
logs/
scripts/
state/
tests/

Important application files include:

scripts/bch_solo_rental_strike_engine.py
dashboard/app.py
config/pools.json

Important deployment scripts include:

scripts/build_dashboard.sh
scripts/check_dashboard.sh
scripts/deploy_dashboard.sh
scripts/restart_dashboard.sh
scripts/update_dashboard.sh

⸻

7. Create Required Directories

Create the runtime directories if they do not already exist:

mkdir -p config logs state

These directories store:

config/   Environment and provider configuration
logs/     Engine execution logs
state/    JSON state and SQLite Recommendation History

⸻

8. Create a Python Virtual Environment

Using the Default Python Version

python3 -m venv venv

Activate it:

source venv/bin/activate

⸻

Using Python 3.13

python3.13 -m venv venv

Activate it:

source venv/bin/activate

The shell prompt should show:

(venv)

Verify the active interpreter:

which python
python --version

⸻

9. Install Python Dependencies

Upgrade the packaging tools:

python -m pip install --upgrade pip setuptools wheel

Install the project requirements:

python -m pip install -r requirements.txt

Verify the most important packages:

python -c "
import numpy
import pandas
import requests
import streamlit
print('Core Python dependencies imported successfully.')
"

The project commonly uses:

* requests
* numpy
* pandas
* scipy
* streamlit
* plotly
* python-dotenv

The exact dependency list is controlled by:

requirements.txt

⸻

10. Configure Environment Variables

Create the environment file:

nano config/.env

A simplified example configuration is shown below.

# ---------------------------------------------------------
# MARKET AND RENTAL DATA
# ---------------------------------------------------------
BRAIINS_BTC_PER_EH_DAY=0.50049
BRAIINS_AVAILABLE_PH=300
# ---------------------------------------------------------
# RENTAL PARAMETERS
# ---------------------------------------------------------
POOL_FEE=0.015
# ---------------------------------------------------------
# STORAGE
# ---------------------------------------------------------
BCH_LOG_DIR=/home/umbrel/bch_rental_engine/logs
BCH_STATE_DIR=/home/umbrel/bch_rental_engine/state
# ---------------------------------------------------------
# TELEGRAM
# ---------------------------------------------------------
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
# ---------------------------------------------------------
# TEST ALERTS
# ---------------------------------------------------------
BCH_FORCE_TEST_ALERT=false

Use paths appropriate for the installation account.

For a development environment, paths may resemble:

/home/coder/projects/bch-rental-engine/logs
/home/coder/projects/bch-rental-engine/state

For Umbrel production, paths may resemble:

/home/umbrel/bch_rental_engine/logs
/home/umbrel/bch_rental_engine/state

Do not commit config/.env to Git.

⸻

11. Load Environment Variables

Load the configuration into the current shell:

set -a
source config/.env
set +a

Verify selected values:

echo "$BCH_LOG_DIR"
echo "$BCH_STATE_DIR"

Sensitive values such as API keys and Telegram tokens should not be printed in shared terminals or screenshots.

⸻

12. Configure Hashpower Providers

Provider configuration is stored in:

config/pools.json

Provider implementations are located under:

scripts/pools/

Current provider modules include:

base.py
braiins.py, when implemented or configured
kryptex.py
mining_dutch.py
molepool.py
two_miners.py

MiningRigRentals support may also require API credentials in config/.env.

At least one usable rental or market-price source must be available for a complete recommendation.

Provider availability may vary over time. The engine should fail clearly or use configured fallback pricing when a required source is unavailable.

⸻

13. Configure Telegram Alerts

Telegram is optional.

Add the following values to config/.env:

TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

Reload the environment:

set -a
source config/.env
set +a

To test Telegram intentionally:

BCH_FORCE_TEST_ALERT=true

Run the engine once, confirm that the alert arrives, and then restore:

BCH_FORCE_TEST_ALERT=false

Do not leave forced test alerts enabled in production.

⸻

14. Compile the Python Code

Before running the engine, verify that the primary files compile:

python -m py_compile \
    scripts/bch_solo_rental_strike_engine.py \
    dashboard/app.py

No output indicates successful compilation.

For development, compile the relevant test files as well:

python -m py_compile tests/*.py

⸻

15. Run the Test Suite

The project follows a Test-Driven Development workflow.

Run all available tests:

pytest -q

Individual test modules can be run during development:

pytest -q tests/test_trends.py
pytest -q tests/test_recommendation_history.py

A production deployment should only use code for which the relevant targeted tests and full regression suite pass.

Current test coverage includes areas such as:

* Recommendation History
* Numeric trends
* Metric trends
* Trend confidence
* Trend persistence
* Trend velocity
* Trend volatility
* Trend strength
* Interpretation behavior
* Opportunity scoring, when present in the current branch

⸻

16. Run the Engine

Load the environment:

set -a
source config/.env
set +a

Run the engine:

python scripts/bch_solo_rental_strike_engine.py

The repository may also provide:

./run_engine.sh

Expected console output may include:

Recommendation: WATCH
Market Regime: FAIR
Opportunity Score: 54.0

The exact recommendation depends on current market conditions.

A successful execution should create or update:

state/bch_solo_rental_strike_engine.json
state/bch_rental_history.sqlite
logs/bch_solo_rental_strike_engine.jsonl

⸻

17. Verify the JSON State

Pretty-print the current engine state:

python -m json.tool \
    state/bch_solo_rental_strike_engine.json

Verify that the output contains the expected decision and market sections, which may include:

* Recommendation
* Opportunity Action
* Opportunity Score
* Market Regime
* Best strike scenario
* Pool recommendation
* Interpretation
* Trend analytics

⸻

18. Verify Recommendation History

Open the SQLite database:

sqlite3 state/bch_rental_history.sqlite

List tables:

.tables

Inspect recent history:

SELECT *
FROM run_history
ORDER BY id DESC
LIMIT 10;

Exit:

.quit

Recommendation History is the foundation for:

* Historical recommendations
* Trend Intelligence
* Dashboard timelines
* Explainability
* Future forecasting
* Strategy backtesting

⸻

19. Current Trend Intelligence

The engine currently supports a reusable trend-analysis pipeline.

Current trend analytics include:

* Direction
* Previous value
* Current value
* Latest change
* History depth
* Confidence
* Persistence
* Velocity
* Volatility
* Trend strength

Current trend-strength classifications include:

* VERY_STRONG
* STRONG
* MODERATE
* UNKNOWN

Trend strength currently considers:

* Direction
* Confidence
* Persistence
* Volatility
* High-velocity promotion logic

Sufficient Recommendation History must exist before all analytics can be populated meaningfully.

⸻

20. Run the Streamlit Dashboard in Development

Activate the virtual environment:

source venv/bin/activate

Load the environment:

set -a
source config/.env
set +a

Start Streamlit:

streamlit run dashboard/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0

Open:

http://SERVER_IP:8501

The dashboard may include:

* Decision Center
* Current recommendation
* Opportunity Score
* Market overview
* Strike analysis
* Pool routing
* Recommendation History
* Historical charts
* Candlestick charts
* Trend interpretation

The engine should be run at least once before the dashboard is expected to contain data.

⸻

21. Install Docker

On Ubuntu or Debian:

sudo apt install docker.io -y

Enable Docker:

sudo systemctl enable docker
sudo systemctl start docker

Verify:

sudo docker --version

Optional: add the current user to the Docker group:

sudo usermod -aG docker "$USER"

Log out and back in before using Docker without sudo.

Umbrel installations may already include Docker.

⸻

22. Build the Dashboard Container

The preferred method is the provided helper script:

./scripts/build_dashboard.sh

Manual build:

docker build \
    -f Dockerfile.dashboard \
    -t bch-rental-dashboard .

Use sudo docker when required by the host configuration.

⸻

23. Deploy the Production Dashboard

The preferred deployment command is:

./scripts/deploy_dashboard.sh

The deployment should create a container named:

bch-rental-dashboard

Manual deployment, when troubleshooting, may resemble:

docker run -d \
    --name bch-rental-dashboard \
    --restart unless-stopped \
    -p 8501:8501 \
    -v "$HOME/bch_rental_engine/state:/root/bch_rental_engine/state" \
    -v "$HOME/bch_rental_engine/config:/root/bch_rental_engine/config" \
    bch-rental-dashboard

Use the repository scripts whenever possible because they contain the project’s expected production configuration.

⸻

24. Verify the Dashboard Container

Check container status:

docker ps

Expected container:

bch-rental-dashboard

Check dashboard health:

./scripts/check_dashboard.sh

View logs:

docker logs bch-rental-dashboard

Follow logs:

docker logs -f bch-rental-dashboard

Open the dashboard:

http://SERVER_IP:8501

⸻

25. Standard Umbrel Production Update

After the initial installation, use the automated update workflow:

ssh umbrel@SERVER_IP
cd ~/bch_rental_engine
./scripts/update_dashboard.sh

The update script is expected to:

1. Verify that the production working tree is clean.
2. Fetch commits and release tags.
3. Pull using fast-forward-only mode.
4. Build the dashboard image.
5. Replace the current dashboard container.
6. Wait for the application to start.
7. Run the health check.

Do not pull unfinished development work directly into production.

⸻

26. Production Helper Scripts

The repository includes operational helpers:

scripts/build_dashboard.sh
scripts/check_dashboard.sh
scripts/deploy_dashboard.sh
scripts/restart_dashboard.sh
scripts/show_version.sh
scripts/update_dashboard.sh
scripts/backup_state.sh

Typical commands:

./scripts/show_version.sh
./scripts/check_dashboard.sh
./scripts/restart_dashboard.sh
./scripts/backup_state.sh

These scripts should be preferred over repeated manual Docker commands.

⸻

27. Configure Scheduled Engine Execution

The engine can be run manually or through a scheduler.

A scheduler may call:

cd ~/bch_rental_engine
./run_engine.sh

Before scheduling, verify that run_engine.sh:

* Loads the correct environment
* Uses the correct Python interpreter
* Writes to the intended state directory
* Writes to the intended log directory
* Returns a nonzero exit code on failure

Potential future operational improvements include:

* Systemd service definitions
* Scheduled reports
* Engine heartbeat monitoring
* Failure alerts
* CI/CD deployment
* Automated release validation

⸻

28. Log Rotation

JSONL logs rotate automatically when configured.

Relevant environment variables may include:

BCH_MAX_JSONL_LOG_BYTES
BCH_MAX_JSONL_LOG_BACKUPS

Typical files:

bch_solo_rental_strike_engine.jsonl
bch_solo_rental_strike_engine.jsonl.1
bch_solo_rental_strike_engine.jsonl.2
bch_solo_rental_strike_engine.jsonl.3

No manual log cleanup should normally be required.

⸻

29. Backups

Back up the following directories:

config/
state/
logs/

The highest-priority operational file is:

state/bch_rental_history.sqlite

This database contains the historical decision record that supports Recommendation History and Trend Intelligence.

Use the provided backup script where available:

./scripts/backup_state.sh

Protect backups containing environment files because they may include credentials.

⸻

30. Installation Verification Checklist

Repository

* Repository cloned successfully
* Correct branch or release checked out
* Working tree clean
* Repository structure verified

Python

* Supported Python version installed
* Virtual environment created
* Virtual environment activates
* Dependencies installed
* Engine compiles
* Dashboard compiles

Configuration

* config/.env created
* Storage paths configured
* Rental-price source configured
* Pool configuration reviewed
* Telegram configured or intentionally disabled
* Secrets excluded from Git

Testing

* Targeted tests pass
* Full test suite passes
* No unexpected warnings
* No local debug code remains

Engine

* Engine runs successfully
* Recommendation generated
* Opportunity Score generated
* JSON state created
* SQLite history created
* JSONL log created
* Recommendation History receives a row

Analytics

* Direction available when history is sufficient
* Confidence calculated
* Persistence calculated
* Velocity calculated
* Volatility calculated
* Trend strength calculated
* Interpretation generated

Dashboard

* Streamlit dashboard starts
* Dashboard is accessible
* Current recommendation displays
* Strike analysis displays
* Recommendation History displays
* Charts render
* Trend analytics render where implemented

Docker

* Docker installed
* Image builds successfully
* Container starts
* Container restart policy configured
* State volume mounted
* Configuration volume mounted
* Health check passes

Optional Services

* Telegram test succeeds
* Scheduled engine execution configured
* Backup procedure tested

⸻

31. Common Installation Problems

Virtual Environment Creation Fails

Example:

ensurepip is not available

Install the matching virtual-environment package:

sudo apt install python3-venv

For Python 3.13:

sudo apt install python3.13-venv

Then recreate the environment.

⸻

ModuleNotFoundError

Ensure the environment is active:

source venv/bin/activate

Reinstall dependencies:

python -m pip install -r requirements.txt

⸻

No Hashpower or Rental Sources Found

Confirm the environment variables are loaded:

set -a
source config/.env
set +a

Review:

config/.env
config/pools.json

Confirm that the selected provider is enabled and configured.

⸻

Dashboard Contains No Data

The engine may not have completed a successful run.

Run:

python scripts/bch_solo_rental_strike_engine.py

Verify:

state/bch_solo_rental_strike_engine.json
state/bch_rental_history.sqlite

⸻

Trend Analytics Are Unknown

This can be normal for a new installation.

Trend analysis requires sufficient historical observations. Allow multiple engine executions to populate Recommendation History.

Also verify:

* SQLite history is updating
* The selected metric is present
* Values are numeric
* History retrieval is returning records

⸻

Port 8501 Is Already in Use

Find the process:

sudo lsof -i :8501

Inspect the existing process before terminating it.

For Docker:

docker ps

A dashboard container may already be running.

⸻

Docker Dashboard Does Not Start

Check:

docker ps -a

Review logs:

docker logs bch-rental-dashboard

Rebuild and redeploy using:

./scripts/build_dashboard.sh
./scripts/deploy_dashboard.sh

⸻

SQLite Is Not Updating

Verify the state directory:

ls -la state

Check that the current user and Docker container have permission to write to it.

Confirm that the engine completed successfully.

⸻

Telegram Alerts Do Not Work

Verify that the environment contains:

TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID

Temporarily test with:

BCH_FORCE_TEST_ALERT=true

Return the setting to false immediately after testing.

⸻

Production Working Tree Is Not Clean

Inspect:

git status

Do not discard production changes without understanding them.

Production should not contain manual source-code changes. Resolve or preserve unexpected files before running the update script.

⸻

32. Current Capabilities

The current installation supports:

* Live market-data retrieval
* BCH network analysis
* Hashpower rental analysis
* Budget and hashrate scenario scoring
* Opportunity Score
* Opportunity Action
* Market regime classification
* Operator recommendation
* Pool routing
* Telegram alerts
* JSON state output
* Rotating JSONL logs
* SQLite Recommendation History
* Historical retrieval
* Trend direction
* Trend confidence
* Trend persistence
* Trend velocity
* Trend volatility
* Trend strength
* High-velocity trend promotion
* Explainable interpretation text
* Streamlit dashboard
* Dockerized Umbrel deployment

⸻

33. Planned Capabilities

Future installation and deployment requirements may expand to support:

Forecast Intelligence

* Trend acceleration
* Trend deceleration
* Reversal detection
* Plateau detection
* False-trend detection
* Forecast confidence
* Early strike opportunity detection

Operational Monitoring

* Engine heartbeat
* Automated health monitoring
* Resource monitoring
* Failure notifications
* Scheduled reports

Deployment Automation

* CI/CD
* Automated release builds
* Release-tag deployment
* Blue-green deployment
* Container health policies
* Systemd integration

Additional Notifications

* Email
* Discord
* Slack
* SMS

Future Analytics

* Historical replay
* Strategy backtesting
* Recommendation stability
* Decision-driver analytics
* Forecast validation
* Multi-coin support

⸻

34. Next Steps

After installation, continue with:

* Configuration Reference⁠￼
* Architecture Guide⁠￼
* Operations Runbook⁠￼
* Recommendation History⁠￼
* Release Checklist⁠￼
* Deployment Guide⁠￼
* Deploy to EC2⁠￼

The system is ready for operational use when the engine runs successfully, Recommendation History updates, the dashboard passes its health check, and all required tests pass.