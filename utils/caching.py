import threading
import time
from typing import Any
from models.meta import SingletonMeta
from loging.log import Log


class CacheItem:
    def __init__(self, data: dict, ttl: int):
        self.data = data
        self.creation_time = time.time()
        self.ttl = ttl

    def is_expired(self):
        return (time.time() - self.creation_time) > self.ttl


class Cache(threading.Thread, metaclass=SingletonMeta):

    def __init__(self):
        super().__init__()
        self.stash = {}
        self._lock = threading.Lock()
        self._exit_flag = threading.Event()

    def cache_item(self, data: Any, item_key: str, ttl: int):
        with self._lock:
            self.stash[item_key] = CacheItem(data, ttl)

    def invalidate_item(self, item_key: str):
        with self._lock:
            del self.stash[item_key]

    def remove_expired_items(self):
        expired_keys = [key for key, item in self.stash.items() if item.is_expired()]
        for key in expired_keys:
            if self.stash[key].is_expired():
                self.invalidate_item(key)

    def run(self):
        while not self._exit_flag.is_set():
            time.sleep(5)
            self.remove_expired_items()

    def stop(self):
        self._exit_flag.set()
        self.join()


def memoize(cache: "Cache", key: str, ttl: int = 300):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if key in cache.stash:
                return cache.stash[key].data
            else:
                cache_data = func(*args, **kwargs)
                cache.cache_item(cache_data, key, ttl)
                return cache_data

        return wrapper

    return decorator


def invalidate(cache: "Cache", key: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache.invalidate_item(key)
            if key in cache.stash:
                cache.invalidate_item(key)
            return func(*args, **kwargs)

        return wrapper

    return decorator
