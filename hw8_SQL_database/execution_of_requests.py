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

    # - Средний балл в потоке.
    cursor.execute("SELECT AVG(grade) FROM grade")
    average_grade = cursor.fetchall()
    print(f'средняя оценка по потоку:  {average_grade[0][0]}')

    # - средний балл в группе по одному предмету.
    subject_id = 27
    cursor.execute(f'SELECT title_subject FROM subject WHERE id={subject_id}')
    subject = cursor.fetchall()
    class_id = 101
    cursor.execute(f"SELECT AVG(grade)\
                   FROM class\
                   INNER JOIN student ON class.id=class_id\
                   INNER JOIN grade ON student.id=student_id\
                   INNER JOIN lesson ON lesson_id=lesson.id\
                   WHERE class.id={class_id} AND subject_id={subject_id}")
    average_grade = cursor.fetchall()
    print(
        f'средний баз по дисциплине "{subject[0][0]}" группы {class_id}: {average_grade[0][0]} ')

    # - Какие курсы читает преподаватель
    # при выбранной модели каждый преподаватель для своей группы читает все предметы (как в GoIT)

    # - Оценки студентов в группе по предмету.

    # - 5 студентов с наибольшим средним баллом по всем предметам.
    cursor.execute("SELECT AVG(grade), name, last_name\
                   FROM student\
                   INNER JOIN grade ON student_id=student.id\
                   GROUP BY id\
                   ORDER BY AVG(grade) DESC\
                   LIMIT 5")
    best_result_5 = cursor.fetchall()
    print(f'5 студентов с наибольшим средним баллом: {best_result_5}')

    # - 1 студент с наивысшим средним баллом по одному предмету.
    subject_id = 28
    cursor.execute(f'SELECT title_subject FROM subject WHERE id={subject_id}')
    subject = cursor.fetchall()
    cursor.execute(f"SELECT AVG(grade), student.name, student.last_name\
                   FROM student\
                   INNER JOIN grade ON student_id=student.id\
                   INNER JOIN lesson ON lesson.id=lesson_id\
                   WHERE subject_id={subject_id}\
                   GROUP BY student.id\
                   ORDER BY AVG(grade) DESC\
                   LIMIT 1")
    best_result_for_subject = cursor.fetchall()
    print(
        f'студент с наибольшим средним баллом по предмету "{subject[0][0]}":  {best_result_for_subject[0]}')

    # - Какие курсы читает преподаватель
    # - Список курсов, которые посещает студент.
    # при выбранной модели каждый преподаватель для своей группы читает все предметы (как в GoIT)
    cursor.execute(f'SELECT * FROM subject')
    subjects = cursor.fetchall()
    for subject in subjects:
        print(
            f'код предмета: {subject[0]}--> название предмета:  {subject[1]}')

    # - Средний балл, который ставит преподаватель.
    # при выббранной модели обучения (преподаватель ведет все предметы в своей группе)
    # средний бал у группе это и есть средний бал, который ставит преподаватель
    class_id = 102
    cursor.execute(
        f'SELECT last_name, name FROM teacher INNER JOIN class ON teacher.id=teacher_id WHERE class.id={class_id}')
    teacher_name = cursor.fetchall()
    cursor.execute(f'SELECT AVG(grade)\
                   FROM student\
                   INNER JOIN grade ON student.id=student_id\
                   WHERE class_id={class_id}')
    average_grade_teacher = cursor.fetchall()
    print(
        f'средний бал всех оценок, выставленных преподавателем {teacher_name[0][0]} {teacher_name[0][1]} равен {average_grade_teacher[0][0]}')

    # - Список курсов, которые студенту читает преподаватель.
    # при выбранной системе - один преподаватель закреплен за группой и ведет в ней все занятия
    # перечень всех курсов это и есть искомый список
    student_id = 455
    cursor.execute(
        f'SELECT name, last_name, class_id FROM student WHERE id={student_id}')
    student_name, student_last_name, class_id = cursor.fetchall()[0]
    cursor.execute(f'SELECT last_name, name\
                   FROM teacher\
                   INNER JOIN class ON teacher.id=teacher_id\
                   WHERE class.id={class_id}')
    teacher_last_name, teacher_name = cursor.fetchall()[0]

    cursor.execute(f'SELECT * FROM subject')
    subjects = cursor.fetchall()
    print(
        f'для студента {student_name}  {student_last_name} преподаватель {teacher_last_name} {teacher_name}')
    print('читает предметы: ')
    for subject in subjects:
        print(
            f'код предмета: {subject[0]}--> название предмета:  {subject[1]}')
    print(student_name, student_last_name, class_id)

# - Оценки студентов в группе по предмету.
# - Оценки студентов в группе по предмету на последнем занятии.
# - Средний балл, который преподаватель ставит студенту.


except (Exception, Error) as error:
    print('Ошибка при работе с PostgreSQL', error)
finally:
    if con:
        cursor.close()
        con.close()
        print("Соединение с PostgreSQL закрыто")
