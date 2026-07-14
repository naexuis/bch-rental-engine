# Deploy to AWS EC2

This guide describes how to deploy the BCH Solo Rental Strike Engine to an Amazon EC2 instance.

Although this guide focuses on AWS EC2, the same process applies to most Linux virtual machines, including:

- DigitalOcean
- Linode
- Vultr
- Azure Virtual Machines
- Google Compute Engine

The deployment consists of two independent components:

1. **BCH Rental Engine** (Python)
2. **Streamlit Dashboard** (Docker)

This separation allows the dashboard to be upgraded independently while the engine continues running.

---

# Recommended EC2 Instance

The engine has modest hardware requirements.

| Component | Recommendation |
|-----------|----------------|
| Instance Type | t3.small or t3.medium |
| vCPUs | 2 |
| Memory | 2–4 GB |
| Storage | 20 GB SSD |
| Operating System | Ubuntu 24.04 LTS |

For larger historical databases or future backtesting, a **t3.large** is recommended.

---

# Network Configuration

Open the following ports in the EC2 Security Group.

| Port | Purpose |
|------|----------|
| 22 | SSH |
| 8501 | Streamlit Dashboard |

Optional:

| Port | Purpose |
|------|----------|
| 443 | HTTPS |
| 80 | Reverse Proxy |

---

# Connect to the Server

SSH into the instance.

```bash
ssh -i my-key.pem ubuntu@YOUR_PUBLIC_IP
```

Update Ubuntu.

```bash
sudo apt update
sudo apt upgrade -y
```

---

# Install Required Packages

Install Git.

```bash
sudo apt install git -y
```

Install Python.

```bash
sudo apt install python3 python3-pip python3-venv -y
```

Install Docker.

```bash
sudo apt install docker.io -y

sudo systemctl enable docker

sudo systemctl start docker
```

Allow your user to run Docker without sudo.

```bash
sudo usermod -aG docker ubuntu
```

Log out and reconnect for the change to take effect.

---

# Clone the Repository

```bash
git clone https://github.com/naexuis/bch-rental-engine.git

cd bch-rental-engine
```

---

# Create the Virtual Environment

```bash
python3 -m venv venv

source venv/bin/activate
```

Install dependencies.

```bash
pip install --upgrade pip

pip install -r requirements.txt
```

---

# Configure the Engine

Create the configuration directory.

```bash
mkdir -p config
```

Create the environment file.

```bash
nano config/.env
```

Example:

```text
BRAIINS_BTC_PER_EH_DAY=0.50049
BRAIINS_AVAILABLE_PH=300

POOL_FEE=0.015

BCH_STATE_DIR=~/bch_rental_engine/state
BCH_LOG_DIR=~/bch_rental_engine/logs

TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Load the variables.

```bash
set -a
source config/.env
set +a
```

---

# Create Runtime Directories

```bash
mkdir -p ~/bch_rental_engine

mkdir -p ~/bch_rental_engine/state

mkdir -p ~/bch_rental_engine/logs
```

Verify.

```bash
tree ~/bch_rental_engine
```

Expected:

```text
bch_rental_engine/

├── logs
└── state
```

---

# Test the Engine

Run:

```bash
python scripts/bch_solo_rental_strike_engine.py
```

Expected:

```
Recommendation: WATCH
```

Confirm the engine created:

```
~/bch_rental_engine/state/

~/bch_rental_engine/logs/
```

---

# Deploy the Dashboard

Build the Docker image.

```bash
docker build \
    -f Dockerfile.dashboard \
    -t bch-rental-dashboard .
```

Run the container.

```bash
docker run -d \
    --name bch-rental-dashboard \
    --restart unless-stopped \
    -p 8501:8501 \
    -v ~/bch_rental_engine/state:/root/bch_rental_engine/state \
    -v ~/bch_rental_engine/config:/root/bch_rental_engine/config \
    bch-rental-dashboard
```

Verify.

```bash
docker ps
```

---

# Access the Dashboard

Open:

```
http://EC2_PUBLIC_IP:8501
```

The following pages should load:

- Market Overview
- Decision Center
- Strike Analysis
- Pool Routing
- Historical Performance
- Candlestick Charts

---

# Configure Automatic Engine Execution

The dashboard only displays the latest engine output.

The engine should therefore run on a schedule.

Example cron job.

Open:

```bash
crontab -e
```

Run every 30 minutes.

```cron
*/30 * * * * cd ~/projects/bch-rental-engine && . venv/bin/activate && set -a && source config/.env && set +a && python scripts/bch_solo_rental_strike_engine.py
```

Adjust the schedule to match your desired refresh interval.

---

# Updating the System

Update the repository.

```bash
git checkout main

git pull origin main
```

Restart the dashboard.

```bash
docker stop bch-rental-dashboard

docker rm bch-rental-dashboard

docker build \
-f Dockerfile.dashboard \
-t bch-rental-dashboard .

docker run -d \
--name bch-rental-dashboard \
--restart unless-stopped \
-p 8501:8501 \
-v ~/bch_rental_engine/state:/root/bch_rental_engine/state \
-v ~/bch_rental_engine/config:/root/bch_rental_engine/config \
bch-rental-dashboard
```

---

# Backup Strategy

Back up the following directories.

```
config/

state/

logs/
```

The most important file is:

```
state/bch_rental_history.sqlite
```

This contains the complete recommendation history.

---

# Restore Procedure

Clone the repository.

Restore:

```
config/

state/

logs/
```

Install dependencies.

Start Docker.

Run the engine.

Launch the dashboard.

No database migration is required.

---

# Security Recommendations

Do not expose SSH to the entire Internet.

Restrict SSH to known IP addresses.

Use SSH keys instead of passwords.

Keep Ubuntu updated.

Do not commit `.env` to Git.

Rotate Telegram credentials if compromised.

Consider placing the dashboard behind Nginx with HTTPS if it will be publicly accessible.

---

# Optional Reverse Proxy

For production deployments, consider placing Streamlit behind Nginx.

Benefits include:

- HTTPS
- Custom domain name
- Authentication
- Rate limiting
- Improved security

Example:

```
dashboard.example.com
```

↓

```
Nginx
```

↓

```
localhost:8501
```

---

# Monitoring

Recommended checks.

Daily:

- Dashboard online
- Engine completed successfully
- SQLite updated
- JSON updated

Weekly:

- Pull latest code
- Review logs
- Verify backups

Monthly:

- Update Ubuntu
- Update Python packages
- Rebuild Docker image

---

# Scaling Considerations

The current architecture is designed for a single server.

Future versions could separate:

- Optimization Engine
- Dashboard
- Database

onto independent servers if computational demands increase.

For the current workload, a single EC2 instance is sufficient.

---

# Verification Checklist

After deployment, verify:

- ✅ EC2 instance reachable via SSH
- ✅ Git installed
- ✅ Python installed
- ✅ Docker installed
- ✅ Repository cloned
- ✅ Virtual environment created
- ✅ Dependencies installed
- ✅ `.env` configured
- ✅ Runtime directories created
- ✅ Engine executes successfully
- ✅ JSON state file created
- ✅ SQLite history database created
- ✅ Dashboard container running
- ✅ Dashboard accessible on port 8501
- ✅ Telegram alerts functioning (optional)
- ✅ Cron job installed
- ✅ Backups configured

If every item above is complete, the BCH Solo Rental Strike Engine is fully operational on AWS EC2.

---

# Future Improvements

Future deployment enhancements may include:

- Docker Compose deployment
- Automatic GitHub Actions deployment
- HTTPS with Let's Encrypt
- Nginx reverse proxy
- CloudWatch monitoring
- Systemd service for the engine
- Automated backup to Amazon S3
- Infrastructure as Code using Terraform

---

# Next Steps

After deployment, continue with:

- [Operations Runbook](OPERATIONS.md)
- [Decision Log](DECISION_LOG.md)
- [Developer Journal](DEVELOPER_JOURNAL.md)
- [Roadmap](ROADMAP.md)