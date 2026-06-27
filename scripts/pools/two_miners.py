from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

from .base import PoolAdapter
from bch_solo_rental_strike_engine import PoolSnapshot


HASHES_PER_PH = 1e15


class TwoMinersAdapter(PoolAdapter):
    def fetch_snapshot(self) -> PoolSnapshot:
        payload = self._fetch_payload()

        return PoolSnapshot(
            name=self.name,
            key=self.key,
            timestamp=datetime.now(timezone.utc).isoformat(),
            hashrate_ph=self._extract_hashrate_ph(payload),
            miners=self._extract_miners(payload),
            fee_pct=self.fee_pct,
            effort_pct=self._extract_effort_pct(payload),
            last_block_minutes=self._extract_last_block_minutes(payload),
            network_hashrate_ph=self._extract_network_hashrate_ph(payload),
            status="ok",
            url=self.url,
        )

    def _fetch_payload(self) -> Dict[str, Any]:
        url = "https://solo-bch.2miners.com/api/stats"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()

    def _extract_hashrate_ph(self, payload: Dict[str, Any]) -> float:
        return float(payload.get("hashrate", 0)) / HASHES_PER_PH

    def _extract_miners(self, payload: Dict[str, Any]) -> Optional[int]:
        value = payload.get("minersTotal")
        return int(value) if value is not None else None

    def _extract_effort_pct(self, payload: Dict[str, Any]) -> Optional[float]:
        value = payload.get("luck")
        return float(value) if value is not None else None

    def _extract_last_block_minutes(self, payload: Dict[str, Any]) -> Optional[float]:
        value = payload.get("stats", {}).get("lastBlockFound")
        if value is None:
            return None

        now_ts = datetime.now(timezone.utc).timestamp()
        return max(0.0, (now_ts - float(value)) / 60)

    def _extract_network_hashrate_ph(self, payload: Dict[str, Any]) -> float:
        nodes = payload.get("nodes", [])

        if not nodes:
            return 0.0

        value = nodes[0].get("networkhashps", 0)
        return float(value) / HASHES_PER_PH