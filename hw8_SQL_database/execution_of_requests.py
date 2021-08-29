# модуль содержит код, который подключается к БД и выполняет все запросы, определенные заданием
import psycopg2


from psycopg2 import Error
from random import choice
from create_db import DATABASE_NAME

try:
    con = psycopg2.connect(
        user="diet",
        password=input('input password for DB'),
        host="81.17.140.55",
        port="5432",
        database=DATABASE_NAME)

    cursor = con.cursor()
    print('Connect to PostgreSQL is success')

    # - Список студентов в группе.
    # получаем перечень групп
    cursor.execute("SELECT id FROM class")
    class_list = cursor.fetchall()

    # выбираем случайным образом группу для которой выводим список студентов
    class_number = choice(class_list)[0]
    cursor.execute(
        f"SELECT name, last_name FROM student WHERE class_id ={class_number}")
    class_list = cursor.fetchall()

    print(f'группа номер {class_number}')
    for student in class_list:
        print(f'--> {student[0]}  {student[1]}')

    # - Какие курсы читает преподаватель
    # при выбранной модели каждый преподаватель для своей группы читает все предметы (как в GoIT)

    # - Оценки студентов в группе по предмету.


# - 5 студентов с наибольшим средним баллом по всем предметам.
# - 1 студент с наивысшим средним баллом по одному предмету.
# - средний балл в группе по одному предмету.
# - Средний балл в потоке.


# - Оценки студентов в группе по предмету.
# - Оценки студентов в группе по предмету на последнем занятии.
# - Список курсов, которые посещает студент.
# - Список курсов, которые студенту читает преподаватель.
# - Средний балл, который преподаватель ставит студенту.
# - Средний балл, который ставит преподаватель.

except (Exception, Error) as error:
    print('Ошибка при работе с PostgreSQL', error)
finally:
    if con:
        cursor.close()
        con.close()
        print("Соединение с PostgreSQL закрыто")
