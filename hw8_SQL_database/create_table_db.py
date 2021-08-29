
import psycopg2


from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# from create_db import
DATABASE_NAME = 'student_db'

try:
    con = psycopg2.connect(
        user="diet",
        password=input('input password for DB'),
        host="81.17.140.55",
        port="5432",
        database=DATABASE_NAME)
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = con.cursor()
    print('Connect to PostgreSQL is success')

    # СОЗДАНИЕ ТАБЛИЦ В СООТВЕСТВИИ С DB_STRUCTURE
    create_table_query = "CREATE TABLE teacher\
            (id SERIAL PRIMARY KEY,\
            last_name text NOT NULL,\
            name text NOT NULL)"
    cursor.execute(create_table_query)
    con.commit()
    print("Таблица teacher успешно создана в PostgreSQL")

    create_table_query = 'CREATE TABLE class\
                    (id INT PRIMARY KEY NOT NULL,\
                    teacher_id INT  REFERENCES teacher (id))'
    cursor.execute(create_table_query)
    con.commit()
    print("Таблица class успешно создана в PostgreSQL")

    create_table_query = "CREATE TABLE student\
            (id SERIAL PRIMARY KEY,\
            last_name text NOT NULL,\
            name text NOT NULL,\
            class_id integer REFERENCES class(id))"
    cursor.execute(create_table_query)
    con.commit()
    print("Таблица student успешно создана в PostgreSQL")

    create_table_query = "CREATE TABLE subject\
            (id SERIAL PRIMARY KEY,\
            title_subject text NOT NULL)"
    cursor.execute(create_table_query)
    con.commit()
    print("Таблица subject успешно создана в PostgreSQL")

    create_table_query = "CREATE TABLE lesson\
            (id SERIAL PRIMARY KEY,\
            date date NOT NULL,\
            subject_id integer REFERENCES subject(id),\
            class_id integer REFERENCES class(id))"
    cursor.execute(create_table_query)
    con.commit()
    print("Таблица lesson успешно создана в PostgreSQL")

    create_table_query = "CREATE TABLE grade\
            (grade integer NOT NULL,\
            lesson_id integer REFERENCES lesson(id),\
            student_id integer REFERENCES student(id))"
    cursor.execute(create_table_query)
    con.commit()
    print("Таблица grade успешно создана в PostgreSQL")

    create_table_query = "CREATE TABLE assignment\
            (class_id integer NOT NULL REFERENCES class(id),\
            teacher_id integer NOT NULL REFERENCES teacher(id),\
            subject_id integer NOT NULL REFERENCES subject(id))"
    cursor.execute(create_table_query)
    con.commit()
    print("Таблица assignment успешно создана в PostgreSQL")

except (Exception, Error) as error:
    print('Ошибка при работе с PostgreSQL', error)
finally:
    if con:
        cursor.close()
        con.close()
        print("Соединение с PostgreSQL закрыто")
