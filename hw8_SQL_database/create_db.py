import psycopg2


from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


DATABASE_NAME = 'student_db'

if __name__ == '__main__':

    try:
        con = psycopg2.connect(
            user="diet",
            password=input('input password for DB'),
            host="81.17.140.55",
            port="5432",
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = con.cursor()
        print('Connect to PostgreSQL is success')

        # СОЗДАНИЕ БАЗЫ ДАННЫХ
        sql_create_database = f'create database {DATABASE_NAME}'
        cursor.execute(sql_create_database)
        print(f'database {DATABASE_NAME} is created')

    except (Exception, Error) as error:
        print('Ошибка при работе с PostgreSQL', error)
    finally:
        if con:
            cursor.close()
            con.close()
            print("Соединение с PostgreSQL закрыто")
