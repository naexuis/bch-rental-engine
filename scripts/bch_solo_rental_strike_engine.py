#!/usr/bin/env python3

from __future__ import annotations

import json
import math
import os
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import hashlib
import hmac
import sqlite3
import requests


# =============================================================================
# CONFIG
# =============================================================================

BASE_DIR = Path.home() / "bch_rental_engine"
CONFIG_DIR = BASE_DIR / "config"
LOG_DIR = BASE_DIR / "logs"
STATE_DIR = BASE_DIR / "state"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
STATE_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = LOG_DIR / "bch_solo_rental_strike_engine.jsonl"
ALERT_LOG_PATH = LOG_DIR / "bch_solo_rental_strike_engine_alerts.jsonl"
STATE_PATH = STATE_DIR / "bch_solo_rental_strike_engine.json"
MRR_LISTINGS_PATH = CONFIG_DIR / "mrr_listings.json"

HISTORY_DB_PATH = STATE_DIR / "bch_rental_history.sqlite"

BUDGET_MIN_USD = float(os.getenv("BCH_STRIKE_BUDGET_MIN_USD", "200"))
BUDGET_MAX_USD = float(os.getenv("BCH_STRIKE_BUDGET_MAX_USD", "300"))
BUDGET_STEP_USD = float(os.getenv("BCH_STRIKE_BUDGET_STEP_USD", "10"))

IDEAL_MIN_HOURS = float(os.getenv("BCH_IDEAL_MIN_HOURS", "1.0"))
IDEAL_MAX_HOURS = float(os.getenv("BCH_IDEAL_MAX_HOURS", "3.0"))
ABSOLUTE_MAX_HOURS = float(os.getenv("BCH_ABSOLUTE_MAX_HOURS", "12.0"))
ALLOW_LONG_RENTALS = os.getenv("BCH_ALLOW_LONG_RENTALS", "true").lower() == "true"

MIN_DURATION_HOURS = IDEAL_MIN_HOURS
MAX_DURATION_HOURS = IDEAL_MAX_HOURS

MRR_ENABLE_API = os.getenv("MRR_ENABLE_API", "false").lower() == "true"
MRR_API_KEY = os.getenv("MRR_API_KEY", "")
MRR_API_SECRET = os.getenv("MRR_API_SECRET", "")
MRR_HASH_MIN_PH = float(os.getenv("MRR_HASH_MIN_PH", "50"))
MRR_HASH_MAX_PH = float(os.getenv("MRR_HASH_MAX_PH", "500"))
MRR_COUNT = int(os.getenv("MRR_COUNT", "100"))

POOL_FEE = float(os.getenv("BCH_POOL_FEE", "0.015"))
ORPHAN_STALE_RISK = float(os.getenv("BCH_ORPHAN_STALE_RISK", "0.005"))
SLIPPAGE_PCT = float(os.getenv("BCH_RENTAL_EXECUTION_SLIPPAGE_PCT", "0.01"))
PRICE_MOVE_BUFFER_PCT = float(os.getenv("BCH_PRICE_MOVE_BUFFER_PCT", "0.01"))

BCH_BLOCK_REWARD_DEFAULT = float(os.getenv("BCH_BLOCK_REWARD", "3.125"))
BLOCKS_PER_DAY = 144

REQUEST_TIMEOUT = int(os.getenv("BCH_REQUEST_TIMEOUT", "20"))
MAX_RETRIES = int(os.getenv("BCH_MAX_RETRIES", "3"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", os.getenv("TELEGRAM_HOME_CHANNEL", ""))

BRAIINS_PRICE_OVERRIDE = os.getenv("BRAIINS_BTC_PER_EH_DAY")
BRAIINS_AVAILABLE_PH = os.getenv("BRAIINS_AVAILABLE_PH")

FORCE_TEST_ALERT = os.getenv("BCH_FORCE_TEST_ALERT", "false").lower() == "true"

POOLS_CONFIG_PATH = Path(os.getenv("BCH_POOLS_CONFIG_PATH", "config/pools.json"))


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class MarketData:
    timestamp: str
    btc_usd: float
    bch_usd: float
    bch_btc: float
    bch_difficulty: float
    bch_network_hashrate_eh: float
    bch_block_reward: float


@dataclass
class HashSource:
    source: str
    name: str
    hashrate_ph: float
    price_btc_per_ph_day: float
    min_hours: float
    max_hours: float
    executable: bool
    rig_id: Optional[str] = None


@dataclass
class StrikeScenario:
    source: str
    name: str
    budget_usd: float
    budget_btc: float
    hashrate_ph: float
    hashrate_eh: float
    duration_hours: float
    cost_btc: float
    cost_usd: float
    expected_blocks: float
    prob_0_blocks: float
    prob_1plus: float
    prob_2plus: float
    expected_bch_gross: float
    expected_bch_net: float
    expected_revenue_usd: float
    expected_profit_usd: float
    roi_pct: float
    risk_adjusted_profit_usd: float
    risk_adjusted_roi_pct: float
    profit_if_0_blocks: float
    profit_if_1_block: float
    profit_if_2_blocks: float
    break_even_price_btc_per_ph_day: float
    current_price_btc_per_ph_day: float
    fair_value_ratio: float
    premium_discount_pct: float
    strike_score: float
    strike_grade: str
    alert_tier: str
    recommendation: str
    strike_type: str

@dataclass
class PoolSnapshot:
    name: str
    key: str

    timestamp: str

    hashrate_ph: float
    miners: Optional[int]

    fee_pct: float

    effort_pct: Optional[float]
    last_block_minutes: Optional[float]

    network_hashrate_ph: float

    status: str

    url: str

# =============================================================================
# HELPERS
# =============================================================================

def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def request_json(url: str, params: Optional[dict] = None) -> Any:
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            last_error = exc
            time.sleep(min(2 ** attempt, 10))

    raise RuntimeError(f"Failed request after {MAX_RETRIES} attempts: {url} | {last_error}")


def request_post_json(url: str, payload: dict) -> Any:
    r = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()


def safe_div(n: float, d: float, default: float = 0.0) -> float:
    return default if d == 0 else n / d


def fmt_usd(x: float) -> str:
    return f"${x:,.2f}"


def fmt_budget_range() -> str:
    return f"{fmt_usd(BUDGET_MIN_USD)}-{fmt_usd(BUDGET_MAX_USD)}"


def fmt_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def poisson_prob_at_least(lam: float, k: int) -> float:
    if lam <= 0:
        return 0.0

    below = 0.0
    for i in range(k):
        below += math.exp(-lam) * (lam ** i) / math.factorial(i)

    return max(0.0, min(1.0, 1.0 - below))


def calculate_network_hashrate(difficulty: float) -> float:
    return difficulty * (2 ** 32) / 600 / 1e18


def classify_strike_grade(fair_value_ratio: float) -> str:
    if fair_value_ratio >= 1.10:
        return "A+"
    if fair_value_ratio >= 1.00:
        return "A"
    if fair_value_ratio >= 0.95:
        return "B"
    if fair_value_ratio >= 0.90:
        return "C"
    if fair_value_ratio >= 0.80:
        return "D"
    return "F"


def classify_alert_tier(
    fair_value_ratio: float,
    risk_adjusted_roi_pct: float,
    prob_1plus: float,
) -> str:
    if fair_value_ratio >= 1.10 and risk_adjusted_roi_pct >= 10:
        return "STRONG_RENT"

    if fair_value_ratio >= 1.03 and risk_adjusted_roi_pct > 0:
        return "DEPLOY_NOW"

    if fair_value_ratio >= 0.98:
        return "NEAR_STRIKE"

    if fair_value_ratio >= 0.90:
        return "WATCH_IMPROVING"

    return "DO_NOT_RENT"

def classify_market_regime(fair_value_ratio: float) -> str:
    if fair_value_ratio >= 1.10:
        return "DEEP_VALUE"
    if fair_value_ratio >= 1.00:
        return "VALUE"
    if fair_value_ratio >= 0.90:
        return "FAIR"
    if fair_value_ratio >= 0.80:
        return "OVERPRICED"
    return "EXTREMELY_OVERPRICED"

def calculate_opportunity_score(
    fair_value_ratio: float,
    prob_1plus: float,
    risk_adjusted_roi_pct: float,
    market_regime: str,
) -> Dict[str, Any]:
    fvr_score = max(0, min(65, fair_value_ratio / 1.10 * 65))
    prob_score = max(0, min(20, prob_1plus / 0.50 * 20))
    roi_score = max(0, min(15, (risk_adjusted_roi_pct + 25) / 35 * 15))

    raw_score = fvr_score + prob_score + roi_score
    score = round(max(0, min(100, raw_score)), 1)

    # Hard caps so bad economics cannot look too attractive.
    if fair_value_ratio < 0.85:
        score = min(score, 39.0)
    elif fair_value_ratio < 0.90:
        score = min(score, 49.0)
    elif risk_adjusted_roi_pct < -10:
        score = min(score, 54.0)
    elif risk_adjusted_roi_pct < 0:
        score = min(score, 69.0)

    if score >= 85:
        action = "STRIKE_NOW"
    elif score >= 70:
        action = "STRONG_WATCH"
    elif score >= 55:
        action = "WATCH"
    elif score >= 40:
        action = "WEAK_WATCH"
    else:
        action = "WAIT"

    return {
        "score": score,
        "action": action,
        "components": {
            "fvr_score": round(fvr_score, 1),
            "prob_score": round(prob_score, 1),
            "roi_score": round(roi_score, 1),
            "market_regime": market_regime,
            "risk_adjusted_roi_pct": risk_adjusted_roi_pct,
            "fair_value_ratio": fair_value_ratio,
        },
    }

def recommendation_from_tier(alert_tier: str) -> str:
    if alert_tier in {"STRONG_RENT", "DEPLOY_NOW"}:
        return "RENT"
    if alert_tier == "NEAR_STRIKE":
        return "NEAR STRIKE"
    if alert_tier == "WATCH_IMPROVING":
        return "WATCH"
    return "DO NOT RENT"


def load_pool_config(path: Path = POOLS_CONFIG_PATH) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        pools = json.load(f)

    return [
        p for p in pools
        if p.get("enabled", True)
    ]

def calculate_pool_dominance(
    rented_hashrate_ph: float,
    existing_pool_hashrate_ph: float,
) -> float:
    total = rented_hashrate_ph + existing_pool_hashrate_ph

    if total <= 0:
        return 0.0

    return rented_hashrate_ph / total

def calculate_pool_network_share(
    rented_hashrate_ph: float,
    existing_pool_hashrate_ph: float,
    network_hashrate_ph: float,
) -> float:

    if network_hashrate_ph <= 0:
        return 0.0

    return (
        rented_hashrate_ph + existing_pool_hashrate_ph
    ) / network_hashrate_ph

# =============================================================================
# TEST FUNCTION
# =============================================================================

def test_pool_math():

    dominance = calculate_pool_dominance(
        rented_hashrate_ph=300,
        existing_pool_hashrate_ph=47,
    )

    print("Dominance:", dominance)

    share = calculate_pool_network_share(
        rented_hashrate_ph=300,
        existing_pool_hashrate_ph=47,
        network_hashrate_ph=3810,
    )

    print("Network Share:", share)

def test_pool_adapters() -> None:
    from scripts.pools import get_pool_adapter

    pools = load_pool_config()

    print(f"Loaded pools: {len(pools)}")

    for pool in pools:
        adapter = get_pool_adapter(pool)
        print(pool.get("key"), type(adapter).__name__)

# =============================================================================
# MARKET DATA
# =============================================================================

def fetch_market_data() -> MarketData:
    prices = request_json(
        "https://api.coingecko.com/api/v3/simple/price",
        params={
            "ids": "bitcoin,bitcoin-cash",
            "vs_currencies": "usd,btc",
        },
    )

    btc_usd = float(prices["bitcoin"]["usd"])
    bch_usd = float(prices["bitcoin-cash"]["usd"])
    bch_btc = float(prices["bitcoin-cash"].get("btc", bch_usd / btc_usd))

    stats = request_json("https://api.blockchair.com/bitcoin-cash/stats")
    data = stats.get("data", stats)

    difficulty = float(
        data.get("difficulty")
        or data.get("blocks_difficulty")
        or data.get("current_difficulty")
    )

    block_reward = float(data.get("block_reward") or BCH_BLOCK_REWARD_DEFAULT)

    return MarketData(
        timestamp=now_utc(),
        btc_usd=btc_usd,
        bch_usd=bch_usd,
        bch_btc=bch_btc,
        bch_difficulty=difficulty,
        bch_network_hashrate_eh=calculate_network_hashrate(difficulty),
        bch_block_reward=block_reward,
    )


# =============================================================================
# HASHPOWER SOURCES
# =============================================================================

def mrr_api_get(endpoint: str, params: Optional[dict] = None) -> dict:
    if not MRR_API_KEY or not MRR_API_SECRET:
        raise RuntimeError("MRR_API_KEY and MRR_API_SECRET must be set in config/.env")

    endpoint_to_sign = endpoint.rstrip("/")
    nonce = str(int(time.time() * 10000))

    sign_string = f"{MRR_API_KEY}{nonce}{endpoint_to_sign}"
    api_sign = hmac.new(
        MRR_API_SECRET.encode("utf-8"),
        sign_string.encode("utf-8"),
        hashlib.sha1,
    ).hexdigest()

    headers = {
        "x-api-key": MRR_API_KEY,
        "x-api-nonce": nonce,
        "x-api-sign": api_sign,
    }

    url = "https://www.miningrigrentals.com/api/v2" + endpoint_to_sign

    r = requests.get(
        url,
        params=params or {},
        headers=headers,
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def as_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def nested_get(obj: dict, paths: List[List[str]], default: Any = None) -> Any:
    for path in paths:
        cur = obj
        ok = True
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                ok = False
                break
            cur = cur[key]
        if ok:
            return cur
    return default


def convert_hashrate_to_ph(hash_value: float, hash_type: str) -> float:
    unit = str(hash_type or "").lower()

    if unit == "eh":
        return hash_value * 1000
    if unit == "ph":
        return hash_value
    if unit == "th":
        return hash_value / 1000
    if unit == "gh":
        return hash_value / 1_000_000
    if unit == "mh":
        return hash_value / 1_000_000_000

    return hash_value


def convert_price_to_btc_per_ph_day(price: float, price_type: str) -> float:
    unit = str(price_type or "").lower()

    if unit == "eh":
        return price / 1000
    if unit == "ph":
        return price
    if unit == "th":
        return price * 1000
    if unit == "gh":
        return price * 1_000_000
    if unit == "mh":
        return price * 1_000_000_000

    # MRR SHA256 often shows BTC/TH/day on the website, so default to TH.
    return price * 1000


def classify_strike_type(duration_hours: float) -> str:
    if duration_hours <= 3:
        return "SHORT_STRIKE"
    if duration_hours <= 6:
        return "EXTENDED_STRIKE"
    if duration_hours <= 12:
        return "LONG_SHOT_SESSION"
    return "REJECT"

def fetch_braiins_source() -> Optional[HashSource]:
    if not BRAIINS_PRICE_OVERRIDE:
        return None

    price_btc_per_eh_day = float(BRAIINS_PRICE_OVERRIDE)
    price_btc_per_ph_day = price_btc_per_eh_day / 1000

    available_ph = float(BRAIINS_AVAILABLE_PH) if BRAIINS_AVAILABLE_PH else 300.0

    return HashSource(
        source="braiins",
        name="Braiins Hashpower",
        hashrate_ph=available_ph,
        price_btc_per_ph_day=price_btc_per_ph_day,
        min_hours=MIN_DURATION_HOURS,
        max_hours=MAX_DURATION_HOURS,
        executable=True,
    )


def fetch_mrr_sources() -> List[HashSource]:
    if not MRR_ENABLE_API:
        return []

    params = {
        "count": MRR_COUNT,
        "type": "sha256",
        "currency": "BTC",
        "rented": "false",
        "offline": "false",
        "islive": "yes",
        "orderby": "price",
        "orderdir": "asc",
        "hash.min": int(MRR_HASH_MIN_PH * 1000),
        "hash.max": int(MRR_HASH_MAX_PH * 1000),
        "hash.type": "th",
    }

    payload = mrr_api_get("/rig", params=params)

    debug_path = STATE_DIR / "mrr_raw_response.json"
    with debug_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    raw = payload.get("data", payload)
    if isinstance(raw, dict) and "records" in raw:
        rigs = raw["records"]
    elif isinstance(raw, dict) and "rigs" in raw:
        rigs = raw["rigs"]
    elif isinstance(raw, list):
        rigs = raw
    else:
        rigs = []

    sources: List[HashSource] = []

    for rig in rigs:
        if not isinstance(rig, dict):
            continue

        status = rig.get("status", {}) or {}

        if status.get("rented") is True:
            continue

        if rig.get("online") is not True:
            continue

        rig_id = str(rig.get("id") or rig.get("rigid") or rig.get("name") or "unknown")
        name = str(rig.get("name") or f"MRR rig {rig_id}")

        hash_value = as_float(
            nested_get(
                rig,
                [
                    ["hashrate", "advertised", "hash"],
                    ["hashrate", "last_5min", "hash"],
                    ["hashrate", "last_15min", "hash"],
                    ["hashrate", "hash"],
                    ["hash", "hash"],
                    ["hashrate"],
                    ["hash"],
                ],
            )
        )

        hash_type = nested_get(
            rig,
            [
                ["hashrate", "advertised", "type"],
                ["hashrate", "last_5min", "type"],
                ["hashrate", "last_15min", "type"],
                ["hashrate", "type"],
                ["hash", "type"],
            ],
            default="ph",
        )

        price_value = as_float(
            nested_get(
                rig,
                [
                    ["price", "BTC", "price"],
                    ["price", "BTC"],
                    ["price"],
                ],
            )
        )

        price_type = nested_get(
            rig,
            [
                ["price", "type"],
                ["rate", "type"],
            ],
            default="ph",
        )

        min_hours = as_float(
            rig.get("minhours")
            or rig.get("min_hours")
            or nested_get(rig, [["price", "BTC", "min_rental_length"]]),
            3.0,
        )

        max_hours = as_float(
            rig.get("maxhours")
            or rig.get("max_hours"),
            ABSOLUTE_MAX_HOURS,
        )

        if hash_value is None or price_value is None:
            continue

        hashrate_ph = convert_hashrate_to_ph(hash_value, str(hash_type))

        if hashrate_ph < MRR_HASH_MIN_PH or hashrate_ph > MRR_HASH_MAX_PH:
            continue

        price_btc_per_ph_day = convert_price_to_btc_per_ph_day(
            price_value,
            str(price_type),
        )

        if hashrate_ph <= 0 or price_btc_per_ph_day <= 0:
            continue

        if min_hours > ABSOLUTE_MAX_HOURS:
            continue

        sources.append(
            HashSource(
                source="mrr",
                name=name,
                hashrate_ph=hashrate_ph,
                price_btc_per_ph_day=price_btc_per_ph_day,
                min_hours=min_hours,
                max_hours=max_hours,
                executable=True,
                rig_id=rig_id,
            )
        )

    return sources


def load_all_sources() -> List[HashSource]:
    sources = []

    braiins = fetch_braiins_source()
    if braiins:
        sources.append(braiins)

    sources.extend(fetch_mrr_sources())

    if not sources:
        raise RuntimeError(
            "No hashpower sources found. Set BRAIINS_BTC_PER_EH_DAY or create config/mrr_listings.json."
        )

    return sources


# =============================================================================
# SCENARIO SCORING
# =============================================================================

def calculate_break_even_price_btc_per_ph_day(market: MarketData) -> float:
    bch_per_eh_day_gross = (
        BLOCKS_PER_DAY
        * market.bch_block_reward
        / market.bch_network_hashrate_eh
    )

    bch_per_eh_day_net = bch_per_eh_day_gross * (1 - POOL_FEE)
    btc_per_eh_day = bch_per_eh_day_net * market.bch_btc

    return btc_per_eh_day / 1000


def build_and_score_scenarios(
    market: MarketData,
    sources: List[HashSource],
) -> List[StrikeScenario]:

    scenarios: List[StrikeScenario] = []

    break_even_price_ph_day = calculate_break_even_price_btc_per_ph_day(market)

    budget = BUDGET_MIN_USD

    while budget <= BUDGET_MAX_USD + 1e-9:
        budget_btc = budget / market.btc_usd

        for source in sources:
            max_affordable_hours = (
                budget_btc
                / (source.hashrate_ph * source.price_btc_per_ph_day)
                * 24
            )

            source_max_allowed_hours = (
                ABSOLUTE_MAX_HOURS
                if source.source == "mrr" and ALLOW_LONG_RENTALS
                else IDEAL_MAX_HOURS
            )

            duration_hours = min(
                max_affordable_hours,
                source.max_hours,
                source_max_allowed_hours,
            )

            min_required_hours = max(source.min_hours, IDEAL_MIN_HOURS)

            if duration_hours < min_required_hours:
                continue

            strike_type = classify_strike_type(duration_hours)

            if strike_type == "REJECT":
                continue

            cost_btc = (
                source.hashrate_ph
                * source.price_btc_per_ph_day
                * duration_hours
                / 24
            )

            cost_usd = cost_btc * market.btc_usd

            if cost_usd > budget + 0.01:
                continue

            hashrate_eh = source.hashrate_ph / 1000
            eh_days = hashrate_eh * (duration_hours / 24)

            expected_blocks = (
                eh_days
                / market.bch_network_hashrate_eh
                * BLOCKS_PER_DAY
            )

            prob_0 = math.exp(-expected_blocks)
            prob_1plus = poisson_prob_at_least(expected_blocks, 1)
            prob_2plus = poisson_prob_at_least(expected_blocks, 2)

            expected_bch_gross = expected_blocks * market.bch_block_reward
            expected_bch_net = (
                expected_bch_gross
                * (1 - POOL_FEE)
                * (1 - ORPHAN_STALE_RISK)
            )

            expected_revenue_usd = expected_bch_net * market.bch_usd
            expected_profit_usd = expected_revenue_usd - cost_usd
            roi_pct = safe_div(expected_profit_usd, cost_usd) * 100

            risk_adjusted_revenue = expected_revenue_usd * (1 - PRICE_MOVE_BUFFER_PCT)
            risk_adjusted_cost = cost_usd * (1 + SLIPPAGE_PCT)
            risk_adjusted_profit = risk_adjusted_revenue - risk_adjusted_cost
            risk_adjusted_roi_pct = safe_div(risk_adjusted_profit, risk_adjusted_cost) * 100

            one_block_value_usd = market.bch_block_reward * (1 - POOL_FEE) * market.bch_usd
            profit_if_0 = -cost_usd
            profit_if_1 = one_block_value_usd - cost_usd
            profit_if_2 = (2 * one_block_value_usd) - cost_usd

            fair_value_ratio = safe_div(
                break_even_price_ph_day,
                source.price_btc_per_ph_day,
            )

            premium_discount_pct = (
                safe_div(source.price_btc_per_ph_day, break_even_price_ph_day, math.inf) - 1
            ) * 100

            duration_penalty = {
                "SHORT_STRIKE": 0,
                "EXTENDED_STRIKE": 5,
                "LONG_SHOT_SESSION": 12,
            }.get(strike_type, 20)

            strike_score = (
                120 * prob_1plus
                + 90 * max(0, fair_value_ratio - 1)
                + 0.35 * risk_adjusted_roi_pct
                - duration_penalty
            )

            grade = classify_strike_grade(fair_value_ratio)
            tier = classify_alert_tier(
                fair_value_ratio=fair_value_ratio,
                risk_adjusted_roi_pct=risk_adjusted_roi_pct,
                prob_1plus=prob_1plus,
            )

            scenarios.append(
                StrikeScenario(
                    source=source.source,
                    name=source.name,
                    strike_type=strike_type,
                    budget_usd=budget,
                    budget_btc=budget_btc,
                    hashrate_ph=source.hashrate_ph,
                    hashrate_eh=hashrate_eh,
                    duration_hours=duration_hours,
                    cost_btc=cost_btc,
                    cost_usd=cost_usd,
                    expected_blocks=expected_blocks,
                    prob_0_blocks=prob_0,
                    prob_1plus=prob_1plus,
                    prob_2plus=prob_2plus,
                    expected_bch_gross=expected_bch_gross,
                    expected_bch_net=expected_bch_net,
                    expected_revenue_usd=expected_revenue_usd,
                    expected_profit_usd=expected_profit_usd,
                    roi_pct=roi_pct,
                    risk_adjusted_profit_usd=risk_adjusted_profit,
                    risk_adjusted_roi_pct=risk_adjusted_roi_pct,
                    profit_if_0_blocks=profit_if_0,
                    profit_if_1_block=profit_if_1,
                    profit_if_2_blocks=profit_if_2,
                    break_even_price_btc_per_ph_day=break_even_price_ph_day,
                    current_price_btc_per_ph_day=source.price_btc_per_ph_day,
                    fair_value_ratio=fair_value_ratio,
                    premium_discount_pct=premium_discount_pct,
                    strike_score=strike_score,
                    strike_grade=grade,
                    alert_tier=tier,
                    recommendation=recommendation_from_tier(tier),
                )
            )

        budget += BUDGET_STEP_USD

    return scenarios


def select_winners(scenarios: List[StrikeScenario]) -> Dict[str, Optional[StrikeScenario]]:
    mrr = [s for s in scenarios if s.source == "mrr"]
    braiins = [s for s in scenarios if s.source == "braiins"]

    winners = {
        "best_strike": max(scenarios, key=lambda s: s.strike_score),
        "best_probability": max(scenarios, key=lambda s: s.prob_1plus),
        "best_fair_value": max(scenarios, key=lambda s: s.fair_value_ratio),
        "best_risk_adjusted_roi": max(scenarios, key=lambda s: s.risk_adjusted_roi_pct),
        "lowest_cost_per_probability": min(
            scenarios,
            key=lambda s: safe_div(s.cost_usd, s.prob_1plus, math.inf),
        ),
        "best_mrr": max(mrr, key=lambda s: s.strike_score) if mrr else None,
        "best_braiins": max(braiins, key=lambda s: s.strike_score) if braiins else None,
    }

    return winners

def build_budget_frontier(scenarios: List[StrikeScenario]) -> List[Dict[str, Any]]:
    frontier = []

    budgets = sorted(set(s.budget_usd for s in scenarios))

    for budget in budgets:
        budget_scenarios = [s for s in scenarios if s.budget_usd == budget]

        if not budget_scenarios:
            continue

        best_probability = max(budget_scenarios, key=lambda s: s.prob_1plus)
        best_score = max(budget_scenarios, key=lambda s: s.strike_score)

        frontier.append({
            "budget_usd": budget,
            "best_probability": {
                "source": best_probability.source,
                "name": best_probability.name,
                "hashrate_ph": best_probability.hashrate_ph,
                "duration_hours": best_probability.duration_hours,
                "cost_usd": best_probability.cost_usd,
                "prob_1plus": best_probability.prob_1plus,
                "prob_2plus": best_probability.prob_2plus,
                "roi_pct": best_probability.roi_pct,
                "risk_adjusted_roi_pct": best_probability.risk_adjusted_roi_pct,
                "fair_value_ratio": best_probability.fair_value_ratio,
                "recommendation": best_probability.recommendation,
            },
            "best_score": {
                "source": best_score.source,
                "name": best_score.name,
                "hashrate_ph": best_score.hashrate_ph,
                "duration_hours": best_score.duration_hours,
                "cost_usd": best_score.cost_usd,
                "prob_1plus": best_score.prob_1plus,
                "prob_2plus": best_score.prob_2plus,
                "roi_pct": best_score.roi_pct,
                "risk_adjusted_roi_pct": best_score.risk_adjusted_roi_pct,
                "fair_value_ratio": best_score.fair_value_ratio,
                "recommendation": best_score.recommendation,
            },
        })

    return frontier

def summarize_budget_frontier(
    budget_frontier: List[Dict[str, Any]],
) -> Dict[str, Any]:
    targets = [0.25, 0.50, 0.75, 0.90]

    summary = {
        "targets": {},
        "best_probability_budget": None,
        "lowest_budget": None,
        "highest_budget": None,
    }

    if not budget_frontier:
        return summary

    summary["lowest_budget"] = budget_frontier[0]["budget_usd"]
    summary["highest_budget"] = budget_frontier[-1]["budget_usd"]

    best_row = max(
        budget_frontier,
        key=lambda r: r["best_probability"]["prob_1plus"],
    )

    summary["best_probability_budget"] = {
        "budget_usd": best_row["budget_usd"],
        "prob_1plus": best_row["best_probability"]["prob_1plus"],
        "source": best_row["best_probability"]["source"],
        "duration_hours": best_row["best_probability"]["duration_hours"],
        "risk_adjusted_roi_pct": best_row["best_probability"]["risk_adjusted_roi_pct"],
        "fair_value_ratio": best_row["best_probability"]["fair_value_ratio"],
    }

    for target in targets:
        matching = [
            row for row in budget_frontier
            if row["best_probability"]["prob_1plus"] >= target
        ]

        if not matching:
            summary["targets"][f"{int(target * 100)}pct"] = None
            continue

        row = min(matching, key=lambda r: r["budget_usd"])
        bp = row["best_probability"]

        summary["targets"][f"{int(target * 100)}pct"] = {
            "budget_usd": row["budget_usd"],
            "prob_1plus": bp["prob_1plus"],
            "source": bp["source"],
            "duration_hours": bp["duration_hours"],
            "risk_adjusted_roi_pct": bp["risk_adjusted_roi_pct"],
            "fair_value_ratio": bp["fair_value_ratio"],
        }

    return summary


# =============================================================================
# REPORTING
# =============================================================================

def scenario_line(s: StrikeScenario) -> str:
    return (
        f"{s.source.upper()} | {s.name} | "
        f"type={s.strike_type}, "
        f"budget={fmt_usd(s.budget_usd)}, "
        f"cost={fmt_usd(s.cost_usd)}, "
        f"hash={s.hashrate_ph:.0f} PH/s, "
        f"duration={s.duration_hours:.2f}h, "
        f"P1+={fmt_pct(s.prob_1plus)}, "
        f"P2+={fmt_pct(s.prob_2plus)}, "
        f"profit={fmt_usd(s.expected_profit_usd)}, "
        f"ROI={s.roi_pct:.2f}%, "
        f"risk ROI={s.risk_adjusted_roi_pct:.2f}%, "
        f"FVR={s.fair_value_ratio:.3f}, "
        f"tier={s.alert_tier}"
    )


def calculate_probability_table(market: MarketData, best_price_btc_per_ph_day: float) -> List[Dict[str, Any]]:
    targets = [0.10, 0.20, 0.25, 0.33, 0.50]

    rows = []

    for p in targets:
        lam = -math.log(1 - p)
        required_eh_days = lam * market.bch_network_hashrate_eh / BLOCKS_PER_DAY
        required_ph_days = required_eh_days * 1000
        required_btc = required_ph_days * best_price_btc_per_ph_day
        required_usd = required_btc * market.btc_usd

        rows.append(
            {
                "target_probability": p,
                "required_usd": required_usd,
                "required_btc": required_btc,
            }
        )

    return rows


def build_alert_message(
    market: MarketData,
    winners: Dict[str, StrikeScenario],
    probability_table: List[Dict[str, Any]],
    opportunity: Dict[str, Any],
    market_regime: str,
    frontier_summary: Dict[str, Any],
    interpretation: str,
) -> str:

    best = winners["best_strike"]

    prob_text = "\n".join(
        f"- {r['target_probability']:.0%}: {fmt_usd(r['required_usd'])}"
        for r in probability_table
    )

    frontier_text = "\n".join(
        f"- {label}: "
        + (
            "not reachable"
            if row is None
            else f"{fmt_usd(row['budget_usd'])}, "
                 f"P1+={fmt_pct(row['prob_1plus'])}, "
                 f"{row['duration_hours']:.2f}h, "
                 f"ROI={row['risk_adjusted_roi_pct']:.2f}%"
        )
        for label, row in frontier_summary.get("targets", {}).items()
    )

    return f"""BCH Solo Rental Strike Report

Timestamp: {market.timestamp}

Question:
Where should I deploy {fmt_budget_range()} for the best short-window BCH solo attempt?

Decision:
Tier: {best.alert_tier}
Recommendation: {best.recommendation}
Strike Grade: {best.strike_grade}
Market Regime: {market_regime}
Opportunity Score: {opportunity['score']}/100
Action: {opportunity['action']}

Interpretation:
{interpretation}

Best Executable Strike:
{scenario_line(best)}

Market:
BTC: {fmt_usd(market.btc_usd)}
BCH: {fmt_usd(market.bch_usd)}
Difficulty: {market.bch_difficulty:,.2f}
Network: {market.bch_network_hashrate_eh:.4f} EH/s

Hashpower:
Current source: {best.source.upper()}
Current price: {best.current_price_btc_per_ph_day:.8f} BTC/PH/day
Break-even price: {best.break_even_price_btc_per_ph_day:.8f} BTC/PH/day
Fair Value Ratio: {best.fair_value_ratio:.3f}
Premium/discount: {best.premium_discount_pct:+.2f}%

Outcome Distribution:
P(0 blocks): {fmt_pct(best.prob_0_blocks)}
P(1+ blocks): {fmt_pct(best.prob_1plus)}
P(2+ blocks): {fmt_pct(best.prob_2plus)}

Outcome Profit:
0 blocks: {fmt_usd(best.profit_if_0_blocks)}
1 block: {fmt_usd(best.profit_if_1_block)}
2 blocks: {fmt_usd(best.profit_if_2_blocks)}

Budget Frontier:
{frontier_text}

Winners:
Best strike: {scenario_line(winners["best_strike"])}
Best probability: {scenario_line(winners["best_probability"])}
Best fair value: {scenario_line(winners["best_fair_value"])}
Best risk ROI: {scenario_line(winners["best_risk_adjusted_roi"])}

Probability Purchase Table:
{prob_text}

Alert Rule:
No probability-only alerts. Telegram only fires for DEPLOY_NOW or STRONG_RENT, unless forced.
"""


def should_alert(best: StrikeScenario, force: bool = False) -> bool:
    if force:
        return True

    return best.alert_tier in {"DEPLOY_NOW", "STRONG_RENT"}

def build_interpretation_text(
    best: StrikeScenario,
    market_regime: str,
    opportunity: Dict[str, Any],
    frontier_summary: Dict[str, Any],
) -> str:
    prob_pct = best.prob_1plus * 100
    fvr = best.fair_value_ratio
    roi = best.risk_adjusted_roi_pct
    action = opportunity.get("action", "UNKNOWN")

    if prob_pct >= 70 and fvr < 0.90:
        return (
            "Probability is high at the larger budget range, but economics still are not good enough to rent. "
            f"The engine estimates a {prob_pct:.2f}% chance of at least one block, but hashpower is still overpriced "
            f"with FVR={fvr:.3f} and risk-adjusted ROI={roi:.2f}%. Recommended action: {action}."
        )

    if prob_pct >= 50 and fvr < 0.90:
        return (
            "The setup has a meaningful block probability, but the rental price is still too expensive relative to expected BCH value. "
            f"P(1+) is {prob_pct:.2f}%, FVR={fvr:.3f}, and risk-adjusted ROI={roi:.2f}%. Recommended action: {action}."
        )

    if fvr >= 1.0 and roi >= 0:
        return (
            "Economics are favorable. Hashpower is priced at or below fair value, and expected return is positive. "
            f"P(1+) is {prob_pct:.2f}%, FVR={fvr:.3f}, and risk-adjusted ROI={roi:.2f}%. Recommended action: {action}."
        )

    if 0.90 <= fvr < 1.0:
        return (
            "The market is close to fair value, but not attractive enough yet. "
            f"P(1+) is {prob_pct:.2f}%, FVR={fvr:.3f}, and risk-adjusted ROI={roi:.2f}%. Recommended action: {action}."
        )

    return (
        "The engine recommends waiting. Current hashpower pricing is not attractive enough relative to BCH reward economics. "
        f"P(1+) is {prob_pct:.2f}%, FVR={fvr:.3f}, market regime is {market_regime}, "
        f"and risk-adjusted ROI is {roi:.2f}%. Recommended action: {action}."
    )

# =============================================================================
# LOGGING
# =============================================================================

def write_jsonl_log(path: Path, record: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str, sort_keys=True) + "\n")


def write_latest_state(path: Path, record: Dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, default=str, sort_keys=True)
    tmp.replace(path)

def init_history_db() -> None:
    with sqlite3.connect(HISTORY_DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS run_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,

                btc_usd REAL,
                bch_usd REAL,
                bch_btc REAL,
                bch_difficulty REAL,
                bch_network_hashrate_eh REAL,

                best_source TEXT,
                best_name TEXT,
                best_hashrate_ph REAL,
                best_duration_hours REAL,
                best_cost_usd REAL,

                best_prob_1plus REAL,
                best_prob_2plus REAL,
                best_expected_profit_usd REAL,
                best_roi_pct REAL,
                best_risk_adjusted_roi_pct REAL,

                best_fair_value_ratio REAL,
                best_premium_discount_pct REAL,
                best_alert_tier TEXT,
                best_recommendation TEXT,

                market_regime TEXT,
                opportunity_score REAL,
                opportunity_action TEXT,

                budget_min_usd REAL,
                budget_max_usd REAL,
                budget_step_usd REAL,

                braiins_price_btc_per_ph_day REAL,
                best_mrr_price_btc_per_ph_day REAL,

                scenario_count INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        existing_cols = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(run_history)"
            ).fetchall()
        }

        new_columns = {
            "market_regime": "TEXT",
            "opportunity_score": "REAL",
            "opportunity_action": "TEXT",
            "budget_min_usd": "REAL",
            "budget_max_usd": "REAL",
            "budget_step_usd": "REAL",
        }

        for col, col_type in new_columns.items():
            if col not in existing_cols:
                conn.execute(
                    f"ALTER TABLE run_history "
                    f"ADD COLUMN {col} {col_type}"
                )

        conn.commit()


def get_best_source_price(sources: List[HashSource], source_name: str) -> Optional[float]:
    prices = [
        s.price_btc_per_ph_day
        for s in sources
        if s.source == source_name and s.price_btc_per_ph_day > 0
    ]
    return min(prices) if prices else None


def write_history_row(
    market: MarketData,
    sources: List[HashSource],
    scenarios: List[StrikeScenario],
    best: StrikeScenario,
    market_regime: str,
    opportunity: Dict[str, Any],
) -> None:
    init_history_db()

    braiins_price = get_best_source_price(sources, "braiins")
    best_mrr_price = get_best_source_price(sources, "mrr")

    with sqlite3.connect(HISTORY_DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO run_history (
                timestamp,
                btc_usd,
                bch_usd,
                bch_btc,
                bch_difficulty,
                bch_network_hashrate_eh,

                best_source,
                best_name,
                best_hashrate_ph,
                best_duration_hours,
                best_cost_usd,

                best_prob_1plus,
                best_prob_2plus,
                best_expected_profit_usd,
                best_roi_pct,
                best_risk_adjusted_roi_pct,

                best_fair_value_ratio,
                best_premium_discount_pct,
                best_alert_tier,
                best_recommendation,

                market_regime,
                opportunity_score,
                opportunity_action,

                budget_min_usd,
                budget_max_usd,
                budget_step_usd,

                braiins_price_btc_per_ph_day,
                best_mrr_price_btc_per_ph_day,

                scenario_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                market.timestamp,
                market.btc_usd,
                market.bch_usd,
                market.bch_btc,
                market.bch_difficulty,
                market.bch_network_hashrate_eh,

                best.source,
                best.name,
                best.hashrate_ph,
                best.duration_hours,
                best.cost_usd,

                best.prob_1plus,
                best.prob_2plus,
                best.expected_profit_usd,
                best.roi_pct,
                best.risk_adjusted_roi_pct,

                best.fair_value_ratio,
                best.premium_discount_pct,
                best.alert_tier,
                best.recommendation,

                market_regime,
                opportunity.get("score"),
                opportunity.get("action"),

                BUDGET_MIN_USD,
                BUDGET_MAX_USD,
                BUDGET_STEP_USD,

                braiins_price,
                best_mrr_price,

                len(scenarios),
            ),
        )
        conn.commit()

def get_history_trends() -> Dict[str, Any]:
    init_history_db()

    windows = {
        "1h": 12,
        "6h": 72,
        "24h": 288,
    }

    metrics = [
        "bch_usd",
        "btc_usd",
        "bch_difficulty",
        "bch_network_hashrate_eh",
        "best_fair_value_ratio",
        "best_prob_1plus",
        "best_roi_pct",
        "braiins_price_btc_per_ph_day",
        "best_mrr_price_btc_per_ph_day",
    ]

    trends = {}

    with sqlite3.connect(HISTORY_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        for label, n_rows in windows.items():
            rows = conn.execute(
                f"""
                SELECT {", ".join(metrics)}
                FROM run_history
                ORDER BY id DESC
                LIMIT ?
                """,
                (n_rows,),
            ).fetchall()

            rows = list(reversed(rows))

            trends[label] = {
                "rows": len(rows),
                "metrics": {},
            }

            if len(rows) < 2:
                continue

            first = rows[0]
            last = rows[-1]

            for metric in metrics:
                start = first[metric]
                end = last[metric]

                if start is None or end is None or start == 0:
                    change_pct = None
                else:
                    change_pct = ((end - start) / start) * 100

                trends[label]["metrics"][metric] = {
                    "start": start,
                    "end": end,
                    "change_pct": change_pct,
                }

    return trends

def send_telegram_alert(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured; skipping alert.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    request_post_json(
        url,
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message[:3900],
            "disable_web_page_preview": True,
        },
    )

    return True


# =============================================================================
# ENGINE
# =============================================================================

def run_engine() -> Dict[str, Any]:
    market = fetch_market_data()
    sources = load_all_sources()

    scenarios = build_and_score_scenarios(market, sources)

    if not scenarios:
        raise RuntimeError("No valid executable strike scenarios found.")

    winners = select_winners(scenarios)
    best = winners["best_strike"]

    budget_frontier = build_budget_frontier(scenarios)
    frontier_summary = summarize_budget_frontier(budget_frontier)

    cheapest_price = min(s.current_price_btc_per_ph_day for s in scenarios)
    probability_table = calculate_probability_table(market, cheapest_price)
    trends = get_history_trends()

    market_regime = classify_market_regime(best.fair_value_ratio)

    opportunity = calculate_opportunity_score(
        fair_value_ratio=best.fair_value_ratio,
        prob_1plus=best.prob_1plus,
        risk_adjusted_roi_pct=best.risk_adjusted_roi_pct,
        market_regime=market_regime,
    )

    write_history_row(
        market=market,
        sources=sources,
        scenarios=scenarios,
        best=best,
        market_regime=market_regime,
        opportunity=opportunity,
    )

    interpretation = build_interpretation_text(
        best=best,
        market_regime=market_regime,
        opportunity=opportunity,
        frontier_summary=frontier_summary,
    )

    answer = (
        f"{best.recommendation}: best executable {fmt_budget_range()} BCH strike is "
        f"{best.source.upper()} {best.name}, {best.hashrate_ph:.0f} PH/s for "
        f"{best.duration_hours:.2f}h, P1+={best.prob_1plus*100:.2f}%, "
        f"risk-adjusted ROI={best.risk_adjusted_roi_pct:.2f}%, "
        f"FVR={best.fair_value_ratio:.3f}, regime={market_regime}, "
        f"opportunity={opportunity['score']}/100, action={opportunity['action']}, "
        f"tier={best.alert_tier}."
    )

    record = {
        "timestamp": market.timestamp,
        "answer": answer,
        "market": asdict(market),
        "sources": [asdict(s) for s in sources],
        "scenario_count": len(scenarios),
        "winners": {k: asdict(v) if v is not None else None for k, v in winners.items()},
        "probability_table": probability_table,
        "recommendation": best.recommendation,
        "alert_tier": best.alert_tier,
        "should_alert": should_alert(best, FORCE_TEST_ALERT),
        "data_sanity_issues": [],
        "config": {
            "budget_min_usd": BUDGET_MIN_USD,
            "budget_max_usd": BUDGET_MAX_USD,
            "budget_step_usd": BUDGET_STEP_USD,
            "min_duration_hours": MIN_DURATION_HOURS,
            "max_duration_hours": MAX_DURATION_HOURS,
            "pool_fee": POOL_FEE,
            "orphan_stale_risk": ORPHAN_STALE_RISK,
            "slippage_pct": SLIPPAGE_PCT,
            "price_move_buffer_pct": PRICE_MOVE_BUFFER_PCT,
        },
        "trends": trends,
        "market_regime": market_regime,
        "opportunity": opportunity,
        "budget_frontier": budget_frontier,
        "frontier_summary": frontier_summary,
        "interpretation": interpretation,
    }

    write_jsonl_log(LOG_PATH, record)
    write_latest_state(STATE_PATH, record)

    if record["should_alert"]:
        message = build_alert_message(
            market=market,
            winners=winners,
            probability_table=probability_table,
            opportunity=opportunity,
            market_regime=market_regime,
            frontier_summary=frontier_summary,
            interpretation=interpretation,
        )
        sent = send_telegram_alert(message)
        record["telegram_sent"] = sent
        write_jsonl_log(ALERT_LOG_PATH, record)
    else:
        record["telegram_sent"] = False

    return record


def main() -> None:
    try:
        result = run_engine()
        best = result["winners"]["best_strike"]

        print("BCH Solo Rental Strike Engine completed.")
        print(result["answer"])
        print(result.get("interpretation", ""))
        print(f"Telegram sent: {result['telegram_sent']}")

    except Exception as exc:
        error_record = {
            "timestamp": now_utc(),
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }

        write_jsonl_log(LOG_PATH, error_record)
        write_latest_state(STATE_PATH, error_record)
        raise


if __name__ == "__main__":
    main()
