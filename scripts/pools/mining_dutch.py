from .base import PoolAdapter


class MiningDutchAdapter(PoolAdapter):
    def fetch_snapshot(self):
        raise NotImplementedError("Mining Dutch adapter not implemented yet")