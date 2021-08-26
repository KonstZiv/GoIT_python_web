
import psycopg2


from faker import Faker
from psycopg2 import Error
from random import randint

fake = Faker('uk_UA')

try:
    con = psycopg2.connect(
        database="students_db",
        user="diet",
        password=input('input password for DB'),
        host="81.17.140.55",
        port="5432"
    )

    print('Database opened successfully')
    cursor = con.cursor()

    groups = (101, 102, 103)
    # заполняем таблицу group и таблицу student
    for group in groups:
        insert_query = f"INSERT INTO public.group (group_number) VALUES ({group})"
        cursor.execute(insert_query)
        con.commit()
        print(f"{group} запись успешно вставлена")
        # Получить результат
        cursor.execute("SELECT * from public.group")
        record = cursor.fetchall()
        print("Результат", record)
        # для соответствующей группы вносим студентов в таблицу student
        for _ in range(30):
            # генерируем студента
            # вносим данные студента в таблицу student
            first_name, last_name = (fake.first_name_male(), fake.last_name_male()) if randint(
                0, 1) else (fake.first_name_female(), fake.last_name_female())
            print(f'{first_name}   {last_name}')
            insert_query = f"INSERT INTO student (last_name, name, group_number) VALUES ('{last_name}', '{first_name}', {group})"
            cursor.execute(insert_query)
            con.commit()
    for _ in range(3):
        # генерируем преподавателя
        # вносим данные преподавателя в таблицу teacher
        first_name, last_name = (fake.first_name_male(), fake.last_name_male()) if randint(
            0, 1) else (fake.first_name_female(), fake.last_name_female())
        print(f'{first_name}   {last_name}')
        insert_query = f"INSERT INTO teacher (last_name, name) VALUES ('{last_name}', '{first_name}')"
        cursor.execute(insert_query)
        con.commit()


except (Exception, Error) as error:
    print('Ошибка при работе с PostgreSQL', error)
finally:
    if con:
        cursor.close()
        con.close()
        print("Соединение с PostgreSQL закрыто")
