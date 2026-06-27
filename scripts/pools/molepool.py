from .base import PoolAdapter


class MolepoolAdapter(PoolAdapter):
    def fetch_snapshot(self):
        raise NotImplementedError("Molepool adapter not implemented yet")