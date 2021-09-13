import redis
db = pass
"""CONFIG SET maxmemory 10mb
CONFIG SET maxmemory-samples 20
CONFIG SET maxmemory-policy allkeys-lru"""

db.config_set('maxmemory', '10mb')
db.config_set('maxmemory-samples', 20)
db.config_set('maxmemory-policy', 'allkeys-lru')


class LruCache:
    def __init__(self, func, max_size, db):
        self.func = func
        self.max_size = max_size
        self.db = db
        self.key = self.func.__name__

    def __call__(self, *args, **kwargs):
        try:
            pass
        except Exception as error:
            print('function arguments must have a method "str"')
            raise error


def lru_cache(max_size=5):
    def wrapper(func):
        cache = LruCache(func, max_size, db)
        return cache
    return wrapper


@lru_cache()
def foo(value: str, value_1: int):
    pass
