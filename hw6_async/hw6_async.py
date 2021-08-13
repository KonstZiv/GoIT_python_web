import asyncio
import aioshutil
import re
import sys


from aiopath import AsyncPath
from asyncio import futures, run, gather
from time import time
from typing import Iterable

UNKNOWN = 'unknown'  # name of catalog for unrecognize files


def normalize(text):  # --> str
    """функция принимает строку и убирает символы "ь" и "'", кирилицу заменяет на латиницу
    в соотвествии с правилами транслитерации украинского языка (пост 55 КМУ 2010 год),
    цифры и латиницу - не трогает, остальные символы заменяет нижним подчерком"""

    def delete_apostrof_soft_sign(text):
        "очищает строку от апострофов, мягких знаков и твердых знаков"

        return text.replace('ь', '').replace("'", "").replace("ъ", "")

    def replaces_comb_zgh(text):
        "заменяет сочетание букв 'зг' на 'zgh' "
        return text.replace('зг', 'zgh').replace('Зг', 'Zgh').replace('зГ', 'zgh')

    def replaces_start_sumbol(text):
        "для букв, транслитерация которых отличается в зависимости от"
        "нахождения буквы в начале/не в начале слова, производит замены для начала слова"
        text = re.sub(r"\b[Є]", 'Ye', text)
        text = re.sub(r"\b[є]", 'ye', text)
        text = re.sub(r"\b[Ї]", 'Yi', text)
        text = re.sub(r"\b[ї]", 'yi', text)
        text = re.sub(r"\b[Й]", 'Y', text)
        text = re.sub(r"\b[й]", 'y', text)
        text = re.sub(r"\b[Ю]", 'Yu', text)
        text = re.sub(r"\b[ю]", 'yu', text)
        text = re.sub(r"\b[Я]", 'Ya', text)
        text = re.sub(r"\b[я]", 'ya', text)
        return text

    def replaces_last_step(text):
        "последняя ступень замен украинских символов на их транслитерацию"
        "!!!!Должна использоваться последней в цепочке преобразований"

        ukr_sumbol_string = 'абвгдежзийклмнопрстуфхцчшщюяєіїґыэ'
        latin_transliter_list = ("a", "b", "v", "h", "d", "e", "zh", "z", "y", "i", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                                 "f", "kh", "ts", "ch", "sh", "shch", "iu", "ia", "ie", "i", "i", "g", "y", "e")
        TRANS = {}
        for c, l in zip(ukr_sumbol_string, latin_transliter_list):
            TRANS[ord(c)] = l
            TRANS[ord(c.upper())] = l.title()
        return text.translate(TRANS)
    text1 = re.sub(r"\W", '_', text)
    return replaces_last_step(replaces_start_sumbol(replaces_comb_zgh(delete_apostrof_soft_sign(text1))))


def get_sort_dist_strukture():
    # формирует структуру для сортировки - имена папок и расширения файлов для перемещения
    return {
        'archives': {'zip', 'gz', 'tar'},
        'music': {'mp3', 'ogg', 'wav', 'amr'},
        'pictures': {'jpeg', 'png', 'jpg', 'svg'},
        'video': {'avi', 'mp4', 'mov', 'mkv'},
        'doc': {'doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'},
        UNKNOWN: {}
    }


async def sort_and_movie(path: AsyncPath, name_of_directory: str, suffixes: set) -> None:
    # функция внутри директории path создает субдиректорию name_of_directory (если ее нет), после этого
    # по пути path рекурсивно ищет все файлы с расширениями из suffixes и измняет их наименование на
    # название с новым каталогом - как бы перемещая в новый каталог. Если названия содержат  кирилические
    # символы - они заменяются на латинские по правилам транскрипирования
    print(f'start {name_of_directory}')
    local_path = path / name_of_directory
    if not await local_path.exists():
        await local_path.mkdir()

    for suffix in suffixes:
        async for elem in path.glob('**/*' + '.' + suffix):
            await elem.replace(local_path / (normalize(elem.stem) + elem.suffix))

    print(f'stop {name_of_directory}')


async def movie_to_unknown(path: AsyncPath, path_to: AsyncPath, ignore_list: list) -> None:
    # По пути path перемещает все неотсортированные на предыдущих шагах файлы в папку path_to.
    # Директории внесенные в ignore_list при этом пропускаются - там файлы не анализируются.
    # Кирилические символы в названиях заменяются на латинские при переносе.
    if not await (path_to).exists():
        await (path_to).mkdir()
    async for elem in path.iterdir():
        is_file = await elem.is_file()
        if is_file:
            await elem.replace(path_to / (normalize(elem.stem) + elem.suffix))
        elif not(elem in ignore_list):
            await movie_to_unknown(elem, path_to, ignore_list)


async def del_empty_dir(path: AsyncPath, ignore_list: list) -> None:
    # Удаляет пустые субдиректории в директории path (рекурсивно). Ignore_list содержит
    # перечень субдиректорий которые программа не просматривает
    async for elem in path.iterdir():
        if not(elem in ignore_list) and await elem.is_dir():
            if not bool([i async for i in elem.rglob('*')]):
                await elem.rmdir()
            else:
                await del_empty_dir(elem, ignore_list)
                await elem.rmdir()


async def unzip_archives(path):
    """функция просматривает архивные файлы в папке 'archives' и если встречает архивы обрабатываемых форматов
    то разархивирует их в субпапки с названием файла архива внутри директории 'archives'"""
    available_arch_type = set()
    for elem in await aioshutil.get_archive_formats():
        available_arch_type.add(elem[0])
    # print('доступные форматы: ', available_arch_type)

    async for elem in (path / 'archives').iterdir():
        # print(f'просматриваю файл - {elem.name}')
        # print(elem.suffix)
        if elem.suffix[1:] in available_arch_type:
            # print(f'найден архив доступного для обработки формата: {elem.name}')
            await aioshutil.unpack_archive(elem, path / 'archives' / elem.stem)
            # print('архив разархивирован')


async def main():
    if len(sys.argv) < 2:
        path_str = input('path = ')
    else:
        path_str = sys.argv[1]

    print(f'будет обработана папка {path_str}')
    print('в ходе обработки файлы будут отсортированы по новым папкам, кирилические символы ')
    print('будут заменены на латиницу, старая структура папок внутри указанной Вами будет уничтожена')
    if input('для продолжения работы скрипта подтвердите действие (y/n): ') == 'y':
        start_time = time()
        path = AsyncPath(path_str)
        if await path.exists():
            if await path.is_dir():
                sort_dict = get_sort_dist_strukture()
                start_removing = time()
                futur = [sort_and_movie(path, key, value)
                         for key, value in sort_dict.items()]
                await gather(*futur)
                #results = []
                # for f in futur:
                #    results.append(asyncio.ensure_future(f))
                # for r in results:
                #    await r
                print(
                    f'общее время перемещения файлов {time() - start_removing}')
                start_unknown = time()
                path_to = path / UNKNOWN
                ignore_list = [path / catalog for catalog in sort_dict]
                await movie_to_unknown(path, path_to, ignore_list)
                print(
                    f'общее время перемещения нераспознаных файлов {time() - start_unknown}')
                start_deleting = time()
                await del_empty_dir(path, ignore_list)
                print(
                    f'общее время удаления пустых папок {time() - start_deleting}')
                start_unpacking = time()
                await unzip_archives(path)
                print(
                    f'общее время разархивирования {time() - start_unpacking}')

            else:
                print(f'{path.absolute} is file')

        else:
            print(f'path {path.absolute()} not exist')
        print(f'общее время работы скрипта {time() - start_time}')


if __name__ == '__main__':
    run(main())
