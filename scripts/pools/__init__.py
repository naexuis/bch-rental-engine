from .base import PoolAdapter
from .molepool import MolepoolAdapter
from .two_miners import TwoMinersAdapter
from .kryptex import KryptexAdapter
from .mining_dutch import MiningDutchAdapter


def get_pool_adapter(config):
    key = str(config.get("key", "")).lower()

    if key == "molepool":
        return MolepoolAdapter(config)

    if key == "2miners":
        return TwoMinersAdapter(config)

    if key == "kryptex":
        return KryptexAdapter(config)

    if key == "mining_dutch":
        return MiningDutchAdapter(config)

    return PoolAdapter(config)