'''
Классы модуля сериализуют/десериаализуют стандартные контейнеры Python в 
бинарный формат и формат Json. Особенность работы класса предназначенного для
работы с Json - при десериализации из формата json в стандартные контейнеры
Python исключаются "искажения типов при двойном преобразовании" 
(Python -> json -> Python) с любой глубиной вложенности: при прохождении цикла
"сериализация-десериализация" кортежи остаются кортежами, множества - множествами
с любой глубиной вложенности контейнеров друг в друга. Ключи в словарях так же 
восстанавливаются до исходного типа
Важно: ключем могут быть объекты типа str, int, float, bool, None
'''

import pickle
import json
from abc import abstractmethod, ABCMeta


pre_dict = {
    str(type(list())):  'list',
    str(type(tuple())): 'tuple',
    str(type(set())):   'set',
    str(type(str())):   'str',
    str(type(int())):   'int',
    str(type(float())): 'float',
    str(type(bool())):  'bool',
    str(type(None)):    'nontype'
}


def pre_error_handler(func):
    # предназначен для фиксации ошибки в ходе сериазизации контейнера в json
    # основная ожидаемая ошибка - несоотвествие типа сериализумеых данных допустимым
    # данным (допустимые данные определяются словарем pre_dict)
    def inner(*args):
        try:
            result = func(*args)
            return result
        except KeyError as message:
            raise KeyError(
                f'Используется недопустимый к сериализации тип данных: {message.args[0]}')
    return inner


@pre_error_handler
def pre_process(data):
    # функция рекурсивно обходит все вложенные контейнеры в исходном контейнере и
    # и в контейнерах, которые подвержены искажениям преобразования сохраняет в нулевом
    # элемеентае исходный тип контейнера, преобразуя все контейнеры (множество и кортеж)
    # к списку
    if isinstance(data, dict):
        cont_res = {}
        for key, value in data.items():
            if not isinstance(value, (set, list, tuple, dict)):
                cont_res[key] = (pre_dict[str(type(key))], value)
            else:
                cont_res[key] = (pre_dict[str(type(key))], pre_process(value))
        return cont_res
    else:
        cont_res = [pre_dict[str(type(data))]]
        for elem in data:
            if not isinstance(elem, (set, list, tuple, dict)):
                cont_res.append(elem)
            else:
                cont_res.append(pre_process(elem))
        return cont_res


def post_process(data):
    # функция рекурсивно обходит все вложенные контейнеры в десериализованном контейнере
    # (и во всех вложенных контейнерах), и в соотвествии с информации об исходном типе
    # контейнера, восстанавливает исходный тип контейнера

    def funk(*args):
        # функция является "заглушкой" - принимает любой аргумент и всегда возвращает None
        # используется для замены литерала 'null' на на None
        return None

    types_dict = {
        'list':     list,
        'tuple':    tuple,
        'set':      set,
        'str':      str,
        'int':      int,
        'float':    float,
        'bool':     bool,
        'nontype':  funk
    }

    if isinstance(data, dict):
        cont_res = {}
        for key, value in data.items():
            if not isinstance(value[1], (list, dict)):
                cont_res[types_dict[value[0]](key)] = value[1]
            else:
                cont_res[types_dict[value[0]](key)] = post_process(value[1])
        return cont_res
    else:
        cont_res = []
        for elem in data[1:]:
            if not isinstance(elem, (list, dict)):
                cont_res.append(elem)
            else:
                cont_res.append(post_process(elem))
        return types_dict[data[0]](cont_res)


class SerializationInterface(metaclass=ABCMeta):
    # абстактиный класс для создания классов сериализации/десериализации контейнеров

    def __init__(self, data) -> None:
        # принимает контейнер, подлежащий сериализации
        pass

    @abstractmethod
    def serialize(self):
        # возвращает сериализованный контейнер, содержащийся в
        pass

    @abstractmethod
    def deserialize(self, serialize_data):
        pass


class ContainerToInBin(SerializationInterface):
    # получает на вход контейнер и, используя методы serialize() - без аргумента -
    # возвращает сериализованный контейнер

    def __init__(self, data=None):
        self.data = data

    def serialize(self):
        return pickle.dumps(self.data) if self.data else None

    def deserialize(self, serialize_data):
        # метод получает на вход бинарный файл и возвращает объект исходный контейнер

        self.data = pickle.loads(serialize_data)
        return self.data


class ContainerToInJson(SerializationInterface):

    def __init__(self, data=None):
        self.data = data

    def serialize(self):
        return json.dumps(pre_process(self.data)) if self.data else None

    def deserialize(self, serialize_data):
        self.data = json.loads(serialize_data)
        return post_process(self.data)


if __name__ == '__main__':

    cont_list = [1, 2, 3, 4, 5, 6, 7, 8]
    cont_dict = {'one': 1, 'two': 2, 'three': 3,
                 'four': 4, 'five': 5, 6: 6, None: 7}
    cont_tuple = (1, 'spam', 1.05, 'fot')
    cont_set = {'one', 'two', 'three', 1, '1'}
    cont_mix = ['1', cont_list, cont_tuple, cont_set, cont_dict]

    assert ContainerToInBin().deserialize(
        ContainerToInBin(cont_list).serialize()) == cont_list, 'List to bin & bin to list: error'

    assert ContainerToInBin().deserialize(
        ContainerToInBin(cont_dict).serialize()) == cont_dict, 'Dict to bin & bin to dict: error'

    assert ContainerToInBin().deserialize(
        ContainerToInBin(cont_tuple).serialize()) == cont_tuple, 'Tuple to bin & bin to tuple: error'

    assert ContainerToInBin().deserialize(
        ContainerToInBin(cont_set).serialize()) == cont_set, 'Set to bin & bin to set: error'

    assert ContainerToInBin().deserialize(
        ContainerToInBin(cont_mix).serialize()) == cont_mix, 'Mix to bin & bin to mix: error'

    assert ContainerToInJson().deserialize(
        ContainerToInJson(cont_list).serialize()) == cont_list, 'List to json & json to list: error'

    assert ContainerToInJson().deserialize(
        ContainerToInJson(cont_dict).serialize()) == cont_dict, 'Dict to json & json to dict: error'

    assert ContainerToInJson().deserialize(
        ContainerToInJson(cont_tuple).serialize()) == cont_tuple, 'Tuple to json & json to tuple: error'

    assert ContainerToInJson().deserialize(
        ContainerToInJson(cont_set).serialize()) == cont_set, 'Set to json & json to set: error'

    assert ContainerToInJson().deserialize(
        ContainerToInJson(cont_mix).serialize()) == cont_mix, 'Mix to json & json to mix: error'

    print(cont_mix)
    print(ContainerToInJson().deserialize(
        ContainerToInJson(cont_mix).serialize()))
