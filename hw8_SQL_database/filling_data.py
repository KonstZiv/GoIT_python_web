import psycopg2

from datetime import datetime, date, timedelta
from faker import Faker
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from random import randint, choice


from create_db import DATABASE_NAME
CLASS_NUMBER = [101, 102, 103]
MAX_STUDENT = 30
MAX_TEACHER = 3
SUBJECT = ['Реляционная алгебра',
           'PostgreSQL и основы языка SQL',
           'Алгоритмы и структуры данных',
           'Основы языка Python',
           'Прикладная математика и информатика']
START_DATA = '01-09-2021'
DURATION_OF_STUDY = 60
LESSON_PER_DAY = 3

if __name__ == '__main__':

    fake = Faker('uk_UA')

    try:
        con = psycopg2.connect(
            user="diet",
            password=input('input password for DB'),
            host="81.17.140.55",
            port="5432",
            database=DATABASE_NAME
        )
        cursor = con.cursor()
        print('Connect to PostgreSQL is success')

        # ЗАПОЛНЯЕМ ТАБЛИЦУ TEACHER
        for _ in range(MAX_TEACHER):
            # генерируем преподавателя
            # вносим данные студента в таблицу teacher
            # radint в тренарном выражении на страже гендерного равенства
            first_name, last_name = (fake.first_name_male(), fake.last_name_male()) if randint(
                0, 1) else (fake.first_name_female(), fake.last_name_female())
            print(f'преподаватель:  {first_name}   {last_name}')
            insert_query = f"INSERT INTO teacher (last_name, name) VALUES ('{last_name}', '{first_name}')"
            cursor.execute(insert_query)
            con.commit()
        print('Таблица teacher заполнена')

        # ЗАПОЛНЯЕМ ТАБЛИЦУ CLASS
        cursor.execute("SELECT id from teacher")
        teachers = cursor.fetchall()
        insert_query = f"INSERT INTO class (id, teacher_id)  \
                        VALUES ({CLASS_NUMBER[0]}, {teachers[0][0]}), \
                                ({CLASS_NUMBER[1]}, {teachers[1][0]}), \
                                ({CLASS_NUMBER[2]}, {teachers[2][0]});"
        cursor.execute(insert_query)
        con.commit()
        print('таблица class заполнена')

        # ЗАПОЛНЯЕМ ТАБЛИЦУ STUDENT
        cursor.execute("SELECT * from class")
        for elem in cursor.fetchall():
            for _ in range(MAX_STUDENT):
                # генерируем студента
                # вносим данные студента в таблицу student
                # radint в тренарном выражении на страже гендерного равенства
                first_name, last_name = (fake.first_name_male(), fake.last_name_male()) if randint(
                    0, 1) else (fake.first_name_female(), fake.last_name_female())
                # print(f'{first_name}   {last_name}')
                insert_query = f"INSERT INTO student (last_name, name, class_id) VALUES ('{last_name}', '{first_name}', {elem[0]})"
                cursor.execute(insert_query)
                con.commit()
        print('Таблица student заполнена')

        # ЗАПОЛНЕНИЕ ТАБЛИЦЫ SUBJECT
        insert_query = f"Insert INTO subject (title_subject) VALUES ('{SUBJECT[0]}'), ('{SUBJECT[1]}'), ('{SUBJECT[2]}'), ('{SUBJECT[3]}'), ('{SUBJECT[4]}')"
        cursor.execute(insert_query)
        con.commit()
        print('Таблица subject заполнена')

        # ЗАПОЛНЕНИЕ ТАБЛИЦЫ lesson
        # в период со START_DATA в течении времени DURATION_OF_STADY у каждой группы по три пары в день,
        # предмет выбирается случайно из числа всех возможных предметов
        date_lesson = datetime.strptime(START_DATA, "%d-%m-%Y").date()
        delta_day = timedelta(days=1)
        cursor.execute("SELECT id from subject")
        id_subject = cursor.fetchall()
        cursor.execute("SELECT id from class")
        id_class = cursor.fetchall()
        for _ in range(DURATION_OF_STUDY):
            for _ in range(LESSON_PER_DAY):
                for id_c in id_class:
                    insert_query = f"Insert INTO lesson(date, subject_id, class_id) VALUES('{date_lesson}', {choice(id_subject)[0]}, {id_c[0]})"
                    cursor.execute(insert_query)
                    con.commit()
            date_lesson = date_lesson + delta_day
        print('Таблица lesson заполнена')
    except (Exception, Error) as error:
        print('Ошибка при работе с PostgreSQL', error)
    finally:
        if con:
            cursor.close()
            con.close()
            print("Соединение с PostgreSQL закрыто")
