import logging
import uuid
from storages import MemoryStorage


class StrategyStorage:
    def __init__(
        self,
        strategiesStorage=MemoryStorage(),
        STRATEGIES_PREFIX='Strategies'
    ):

        self.strategiesStorage = strategiesStorage
        self.STRATEGIES_PREFIX = STRATEGIES_PREFIX

    def get_strategy(self, uid, type):
        json = self.strategiesStorage.get(self.STRATEGIES_PREFIX, uid)
        logging.debug(f"storage: {self.strategiesStorage}")
        logging.debug(f"uid: {uid}")
        logging.debug(f"recieved: {json}")
        if not json:
            return None
        st = type()

        st.from_json(json)
        logging.debug(st.players)
        return st

    def save_strategy(self, strategy, uid=None):
        logging.debug(f"storage: {self.strategiesStorage}")
        logging.debug(f"uid: {uid}")

        if not uid:
            uid = str(uuid.uuid4())
        strategy.uid = uid
        json = strategy.to_json()
        self.strategiesStorage.save(
            self.STRATEGIES_PREFIX, uid, json)
        logging.debug(f"Saved: {json}")
        return uid
