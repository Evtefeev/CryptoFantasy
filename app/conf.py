import dotenv
from app.storages import MemoryStorage, RedisStorage
import os

dotenv.load_dotenv()



ENABLE_CHEAT = False
# STORAGE = MemoryStorage()
# STORAGE = RedisStorage()
# USE_REDIS = False
USE_REDIS = False if os.environ.get('USE_REDIS') == 'False' else True

# if USE_REDIS is None:
#     USE_REDIS = True

if USE_REDIS:
    STORAGE = RedisStorage()
else:
    STORAGE = MemoryStorage()