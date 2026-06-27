from dataclasses import dataclass
from typing import Any, Dict


class PoolAdapter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @property
    def key(self) -> str:
        return str(self.config.get("key", ""))

    @property
    def name(self) -> str:
        return str(self.config.get("name", self.key))

    @property
    def url(self) -> str:
        return str(self.config.get("url", ""))

    @property
    def fee_pct(self) -> float:
        return float(self.config.get("fee_pct", 0.0))

    def fetch_snapshot(self):
        raise NotImplementedError