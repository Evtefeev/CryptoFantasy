from app.storages import MemoryStorage, RedisStorage

ENABLE_CHEAT = False
STORAGE = MemoryStorage()
# STORAGE = RedisStorage()
# USE_REDIS = False
USE_REDIS = True