from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

from .base import PoolAdapter

try:
    from scripts.bch_solo_rental_strike_engine import PoolSnapshot
except ModuleNotFoundError:
    from bch_solo_rental_strike_engine import PoolSnapshot


HASHES_PER_PH = 1e15


class MolepoolAdapter(PoolAdapter):
    def fetch_snapshot(self) -> PoolSnapshot:
        payload = self._fetch_payload()
        result = payload.get("result", {})

        hashrate_ph = self._extract_hashrate_ph(result)
        network_hashrate_ph = self._extract_network_hashrate_ph(result)
        miners = self._extract_miners(result)

        return PoolSnapshot(
            name=self.name,
            key=self.key,
            timestamp=datetime.now(timezone.utc).isoformat(),
            hashrate_ph=hashrate_ph,
            miners=miners,
            fee_pct=float(result.get("fee", self.fee_pct)),
            effort_pct=self._extract_effort_pct(result),
            last_block_minutes=self._extract_last_block_minutes(result),
            network_hashrate_ph=network_hashrate_ph,
            status="ok",
            url=self.url,
        )

    def _fetch_payload(self) -> Dict[str, Any]:
        url = "https://bch.molepool.com/api/v1/stats"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()

    def _extract_hashrate_ph(self, result: Dict[str, Any]) -> float:
        return float(result.get("totalHashrate", 0)) / HASHES_PER_PH

    def _extract_network_hashrate_ph(self, result: Dict[str, Any]) -> float:
        return float(result.get("networkHashrate", 0)) / HASHES_PER_PH

    def _extract_miners(self, result: Dict[str, Any]) -> Optional[int]:
        value = result.get("totalMiners")
        return int(value) if value is not None else None

    def _extract_effort_pct(self, result: Dict[str, Any]) -> Optional[float]:
        value = result.get("currentEffort")
        return float(value) * 100 if value is not None else None

    def _extract_last_block_minutes(self, result: Dict[str, Any]) -> Optional[float]:
        value = result.get("lastBlockFound")
        if value is None:
            return None

        now_ts = datetime.now(timezone.utc).timestamp()
        return max(0.0, (now_ts - float(value)) / 60)