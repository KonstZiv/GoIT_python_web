import redis

db = redis.Redis(
    host='localhost',
    port=6379,
    db=0
)


class LruCache:
    def __init__(self, func, max_size, db):
        self.func = func
        self.max_size = max_size
        self.db = db
        self.key = self.func.__name__

    def __call__(self, *args, **kwargs):
        try:
            # получаем строковое выражение аргументов функции
            func_param = ''
            for i in args:
                func_param += f':{str(i)}'
            for key, value in kwargs.items():
                func_param += f':{str(key)}\{str(value)}'
            # получаем полное имя для хранения результата, включающее как имя функции так и строковые значения параметров
            full_key = f'{self.key}::{func_param}'
            # print(full_key)
            if self.db.get(full_key):
                # значение функции есть в кэше
                res = self.db.get(full_key)
                print('из кэша')
            else:
                # значения функции нет в кэше
                res = self.func(*args, **kwargs)
                self.db.set(full_key, res)
                print('в кэше не было')
            # убираем из очереди этой же функции такой же вызов, если он есть
            self.db.lrem(self.key, -1, func_param)
            # вносим в очередь, соотвествующую этой функции, последний вызов - первым
            self.db.lpush(self.key, func_param)
            # проверяем длину очереди. Если она больше чем self.max_size, то убираем последний элемент в очереди и
            # уничтожаем соотвествую ему запись в БД
            if self.db.llen(self.key) > self.max_size:
                last_elem = self.db.rpop(self.key)
                self.db.delete(f'{self.key}::{last_elem}')
            print(f'новая очередь: {self.db.lrange(self.key, 0, -1)}')
            return res
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

    return f'result_{value}  {value_1}'


@lru_cache()
def funk_1(*args):
    return f'funk_1 {args}'


def funk_2(**kwargs):
    return kwargs


if __name__ == '__main__':

    for i in range(5):
        print(funk_1(i))

    print(funk_1(3))

    print(funk_1(1))
