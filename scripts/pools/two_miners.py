from .base import PoolAdapter


class TwoMinersAdapter(PoolAdapter):
    def fetch_snapshot(self):
        raise NotImplementedError("2Miners adapter not implemented yet")