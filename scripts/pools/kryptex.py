from .base import PoolAdapter


class KryptexAdapter(PoolAdapter):
    def fetch_snapshot(self):
        raise NotImplementedError("Kryptex adapter not implemented yet")