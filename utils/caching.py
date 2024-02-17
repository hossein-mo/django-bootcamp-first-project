import threading
import time
from typing import Any
from models.meta import SingletonMeta


class CacheItem:
    def __init__(self, data: dict, ttl: int):
        """Creates a object of CacheItem type

        Args:
            data (dict): data to store
            ttl (int): time to live 
        """        
        self.data = data
        self.creation_time = time.time()
        self.ttl = ttl

    def is_expired(self) -> bool:
        """Checks if  time to live has passed for item or not

        Returns:
            bool: True if time to live has passed
        """      
        return (time.time() - self.creation_time) > self.ttl


class Cache(threading.Thread, metaclass=SingletonMeta):

    def __init__(self):
        """Constructor for Cache thread
        """        
        super().__init__()
        self.stash = {}
        self._lock = threading.Lock()
        self._exit_flag = threading.Event()

    def cache_item(self, data: Any, item_key: str, ttl: int):
        """Creates a cache item and stores it in stash

        Args:
            data (Any): data to cache
            item_key (str): key of item in stash
            ttl (int): time to live
        """        
        with self._lock:
            self.stash[item_key] = CacheItem(data, ttl)

    def invalidate_item(self, item_key: str):
        """Removes cache item from stash

        Args:
            item_key (str): key of the cache item
        """        
        with self._lock:
            del self.stash[item_key]

    def remove_expired_items(self):
        """Removes cache items that their ttl has passed
        """        
        expired_keys = [key for key, item in self.stash.items() if item.is_expired()]
        for key in expired_keys:
            if self.stash[key].is_expired():
                self.invalidate_item(key)

    def run(self):
        """Runs the caching thread, the thread only checks removes expired cache items every 5 seconds
        """        
        while not self._exit_flag.is_set():
            time.sleep(5)
            self.remove_expired_items()

    def stop(self):
        """Function to stop caching thread
        """        
        self._exit_flag.set()
        self.join()


def memoize(cache: "Cache", key: str, ttl: int = 300):
    """Decorator to use stored cache items or get them from cache if exist

    Args:
        cache (Cache): Cache instance
        key (str): key of cache item
        ttl (int, optional): Time to live of new items. Defaults to 300.
    """    
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
    """Invalidates related cache item.

    Args:
        cache (Cache): Cache instance
        key (str): key of the cached item
    """    
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache.invalidate_item(key)
            if key in cache.stash:
                cache.invalidate_item(key)
            return func(*args, **kwargs)

        return wrapper

    return decorator
