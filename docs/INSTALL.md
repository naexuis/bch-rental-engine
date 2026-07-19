# Installation Guide

This guide walks through installing the BCH Rental Engine on a brand-new Linux server.

The engine has been developed and tested on Ubuntu-based systems and Umbrel OS, but it is designed to be portable to any modern Linux distribution, cloud virtual machine (AWS EC2, Azure, DigitalOcean, Vultr, Linode, etc.), or local workstation.

Estimated installation time: **15–30 minutes**

---

# 1. Supported Operating Systems

The BCH Rental Engine has been tested on:

| Operating System | Status |
|------------------|--------|
| Ubuntu 22.04 LTS | ✅ Recommended |
| Ubuntu 24.04 LTS | ✅ Recommended |
| Umbrel OS | ✅ Tested |
| Debian 12 | ✅ Expected to work |
| Raspberry Pi OS (64-bit) | ⚠️ Limited testing |
| macOS | ⚠️ Development only |
| Windows (WSL2) | ⚠️ Development only |

The project assumes a Linux environment and Bash shell.

---

# 2. Install Git

Git is used to download and update the project.

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install git -y
```

Verify installation:

```bash
git --version
```

Example:

```
git version 2.43.0
```

---

# 3. Install Python

Python 3.11 or newer is recommended.

Ubuntu:

```bash
sudo apt install python3 python3-pip python3-venv -y
```

Verify:

```bash
python3 --version
```

Example:

```
Python 3.13.1
```

---

# 4. Clone the Repository

Clone the repository into your home directory.

```bash
git clone https://github.com/naexuis/bch-rental-engine.git

cd bch-rental-engine
```

Verify:

```bash
ls
```

You should see folders similar to:

```
config/
dashboard/
docs/
scripts/
README.md
requirements.txt
```

---

# 5. Create a Virtual Environment

A Python virtual environment isolates project dependencies from the operating system.

Create the environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Your prompt should now begin with:

```
(venv)
```

---

# 6. Install Python Packages

Upgrade pip:

```bash
pip install --upgrade pip
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

Verify installation:

```bash
pip list
```

Required packages include:

- requests
- streamlit
- plotly
- pandas
- numpy

---

# 7. Configure Environment Variables

Create the environment file:

```bash
mkdir -p config

nano config/.env
```

Example configuration:

```text
BRAIINS_BTC_PER_EH_DAY=0.50049
BRAIINS_AVAILABLE_PH=300

POOL_FEE=0.015

BCH_LOG_DIR=~/bch_rental_engine/logs
BCH_STATE_DIR=~/bch_rental_engine/state
```

Save the file.

Load the variables:

```bash
set -a
source config/.env
set +a
```

Verify:

```bash
echo $BRAIINS_BTC_PER_EH_DAY
```

---

# 8. Configure Telegram (Optional)

Telegram alerts are optional but recommended.

Create a Telegram bot using BotFather.

Add the following variables to `.env`:

```text
TELEGRAM_BOT_TOKEN=xxxxxxxxxxxxxxxx
TELEGRAM_CHAT_ID=123456789
```

Verify:

```bash
echo $TELEGRAM_CHAT_ID
```

If omitted, the engine will continue running without sending alerts.

---

# 9. Configure Pool Sources

The engine supports multiple hashpower providers.

Currently supported:

- Braiins
- MiningRigRentals

At least one provider must be configured.

Example:

```text
BRAIINS_BTC_PER_EH_DAY=0.50049
BRAIINS_AVAILABLE_PH=300
```

If using MiningRigRentals, configure the required API credentials in `.env` according to the configuration guide.

---

# 10. Run the Engine

Load environment variables:

```bash
set -a
source config/.env
set +a
```

Run:

```bash
python scripts/bch_solo_rental_strike_engine.py
```

Expected output:

```
Recommendation: WATCH

Market Regime: FAIR

Opportunity Score: 54.0
```

Successful execution creates:

```
state/
logs/
```

and writes:

```
bch_solo_rental_strike_engine.json
bch_rental_history.sqlite
```

---

# 11. Run the Dashboard

Start Streamlit:

```bash
streamlit run dashboard/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0
```

Open your browser:

```
http://SERVER_IP:8501
```

The dashboard should display:

- Current Recommendation
- Market Overview
- Decision Center
- Strike Analysis
- Pool Routing
- Historical Performance
- Candlestick Charts

---

# 12. Docker Installation

Install Docker.

Ubuntu:

```bash
sudo apt install docker.io -y

sudo systemctl enable docker

sudo systemctl start docker
```

Verify:

```bash
docker --version
```

---

# 13. Docker Deployment

Build the dashboard:

```bash
docker build \
    -f Dockerfile.dashboard \
    -t bch-rental-dashboard .
```

Run:

```bash
docker run -d \
    --name bch-rental-dashboard \
    --restart unless-stopped \
    -p 8501:8501 \
    -v ~/bch_rental_engine/state:/root/bch_rental_engine/state \
    -v ~/bch_rental_engine/config:/root/bch_rental_engine/config \
    bch-rental-dashboard
```

Check status:

```bash
docker ps
```

Expected:

```
STATUS

Up
```

---

# 14. Common Problems

## No hashpower sources found

```
RuntimeError:
No hashpower sources found
```

Cause:

Environment variables have not been loaded.

Solution:

```bash
set -a
source config/.env
set +a
```

---

## ModuleNotFoundError

Install packages:

```bash
pip install -r requirements.txt
```

---

## Dashboard shows no data

Cause:

The engine has never been run.

Run:

```bash
python scripts/bch_solo_rental_strike_engine.py
```

---

## Port 8501 already in use

Find the process:

```bash
lsof -i :8501
```

Terminate it:

```bash
kill PID
```

---

## Docker dashboard won't start

View logs:

```bash
docker logs bch-rental-dashboard
```

---

## Telegram alerts not working

Verify:

```
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

are correctly configured.

---

# 15. Verification Checklist

After installation, verify the following:

- ✅ Python virtual environment activates successfully
- ✅ Dependencies install without errors
- ✅ Environment variables load correctly
- ✅ Engine runs successfully
- ✅ JSON state file created
- ✅ SQLite history database created
- ✅ JSONL log file created
- ✅ Dashboard loads in browser
- ✅ Market data displayed
- ✅ Decision Center populated
- ✅ Strike Analysis populated
- ✅ Pool Routing displayed
- ✅ Historical charts display
- ✅ Candlestick charts load
- ✅ Telegram alerts (optional) working
- ✅ Docker container starts successfully (optional)

If every item above is complete, the BCH Rental Engine is fully installed and ready for use.

# Next Steps

Once the engine is installed, continue with the following guides:

- [Configuration Reference](CONFIGURATION.md)
- [Architecture Guide](ARCHITECTURE.md)
- [Operations Runbook](OPERATIONS.md)
- [Deploy to EC2](DEPLOY_EC2.md)