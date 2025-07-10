
from abc import ABC, abstractmethod
import os
import pickle
import dotenv
import redis


dotenv.load_dotenv()

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_DB = os.environ.get('REDIS_DB')
REDIS_URL = os.environ.get('REDIS_URL')

class Storage(ABC):
    @abstractmethod
    def save(self, type: str, label: str, obj: bytes):
        pass

    @abstractmethod
    def get(self, type: str, label: str) -> bytes:
        pass


class MemoryStorage(Storage):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MemoryStorage, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.data = {}
            self._initialized = True

    def save(self, type: str, label: str, obj: bytes):
        if type not in self.data:
            self.data[type] = {}
        self.data[type][str(label)] = obj  # ключ — строка

    def get(self, type: str, label: str) -> bytes:
        return self.data.get(type, {}).get(str(label), None)
    
    def clear(self):
        self.data.clear()


def MemoryStorageTest():
    return MemoryStorage()


class RedisStorage(Storage):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB):
        # self.redis = redis.StrictRedis(host=host, port=port, db=db)
        self.redis = redis.Redis.from_url(REDIS_URL)

    def _make_key(self, type: str, label: str) -> str:
        return f"{type}:{label}"

    def save(self, type: str, label: str, obj: object):
        key = self._make_key(type, label)
        data = pickle.dumps(obj)
        self.redis.set(key, data)

    def get(self, type: str, label: str) -> object:
        key = self._make_key(type, label)
        data = self.redis.get(key)
        if data is not None:
            return pickle.loads(data)
        return None
