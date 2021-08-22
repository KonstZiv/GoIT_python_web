import psycopg2
import os

con = psycopg2.connect(
    database="students_and_grades",
    user="diet",
    password=input('input password for DB'),
    host="81.17.140.55",
    port="5432"
)


print('Database opened successfully')
