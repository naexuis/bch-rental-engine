from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

from .base import PoolAdapter

try:
    from scripts.bch_solo_rental_strike_engine import PoolSnapshot
except ModuleNotFoundError:
    from bch_solo_rental_strike_engine import PoolSnapshot


HASHES_PER_PH = 1e15


class KryptexAdapter(PoolAdapter):
    def fetch_snapshot(self) -> PoolSnapshot:
        payload = self._fetch_payload()

        return PoolSnapshot(
            name=self.name,
            key=self.key,
            timestamp=datetime.now(timezone.utc).isoformat(),
            hashrate_ph=self._extract_hashrate_ph(payload),
            miners=self._extract_miners(payload),
            fee_pct=self._extract_solo_fee_pct(payload),
            effort_pct=None,
            last_block_minutes=None,
            network_hashrate_ph=self._extract_network_hashrate_ph(payload),
            status="ok",
            url=self.url,
        )

    def _fetch_payload(self) -> Dict[str, Any]:
        url = "https://pool.kryptex.com/bch/api/v1/pool/info"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()

    def _extract_hashrate_ph(self, payload: Dict[str, Any]) -> float:
        return float(payload.get("hashrate", 0)) / HASHES_PER_PH

    def _extract_miners(self, payload: Dict[str, Any]) -> Optional[int]:
        value = payload.get("miners")
        return int(value) if value is not None else None

    def _extract_solo_fee_pct(self, payload: Dict[str, Any]) -> float:
        commission = payload.get("commission", {})

        if isinstance(commission, dict) and "SOLO" in commission:
            return float(commission["SOLO"]) * 100

        return self.fee_pct

    def _extract_network_hashrate_ph(self, payload: Dict[str, Any]) -> float:
        return float(payload.get("net_hashrate", 0)) / HASHES_PER_PH