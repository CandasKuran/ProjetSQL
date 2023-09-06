import mysql.connector
import datetime
import csv
from datetime import datetime, timedelta



import database


def open_db():
    return mysql.connector.connect(host='127.0.0.1', port='3306',
                                   user='root', password='',
                                   database='classroom_cleanings',
                                   buffered=True, autocommit=True)


db_connection = open_db()


def get_students():
    query = "SELECT id,firstname, lastname,class_id FROM students"
    cursor = db_connection.cursor()
    cursor.execute(query)  #, multi=True
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_student(id):
    query = "SELECT firstname, lastname FROM students WHERE id = %s"
    cursor = db_connection.cursor()
    cursor.execute(query, (id,))
    row = cursor.fetchone()
    cursor.close()
    return row


def add_student(firstname, lastname, class_id=1):


    query = "INSERT INTO students (firstname, lastname, class_id) values (%s, %s, %s)"
    cursor = db_connection.cursor()
    cursor.execute(query, (firstname, lastname, class_id))
    inserted_id = cursor.lastrowid
    cursor.close()
    return inserted_id



def get_all_classes():
    query = "SELECT id, name FROM classes"
    cursor = db_connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return rows

def get_tasks():
    query = "SELECT id, week_number, student_id FROM tasks"
    cursor = db_connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def add_class(name):
    query = "INSERT INTO classes (name) VALUES (%s)"
    cursor = db_connection.cursor()
    values = (name,)
    cursor.execute(query, values)
    cursor.close()




# on a pris les donnes de classes depuis notre base de donnees. et on a cree nouvelle tube quilsappelle class_name_to_id{}
# et on l'a mis les tout les donnes de classes.
# apres avec un loup on va controler les noms et id.
def classnameID():
    class_name_to_id = {}
    query = "SELECT id, name FROM classes"
    cursor = db_connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    for class_row in rows:
        id,name = class_row
        class_name_to_id[name] = id
    return class_name_to_id


def importercsvClass():
    # pour ouvrir fichier csv et lire separation avec separateur ';' => delimiter=';'
    with open('classes.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')

        # on a cree un loup pour prendre les donnes dans le fichier csv
        for row in csv_reader:
            class_name = row['Nom']
            add_class(name=class_name)

# avec fonction  classnameID on a deja verifier les noms et id. avec cet fonction on control le fichier csv et notre base de donnes
def importercsvStudent():
    class_name_to_id = classnameID()
    # pour ouvrir fichier csv et lire separation avec separateur ';' => delimiter=';'
    with open('students.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')

        # on a cree un loup pour prendre les donnes dans le fichier csv
        for row in csv_reader:
            first_name = row['Prénom']
            last_name = row['Nom']
            class_name = row['Classe']

            if class_name in class_name_to_id:
                class_id = class_name_to_id[class_name]

                add_student(firstname=first_name, lastname=last_name, class_id=class_id)
            else:
                print(f"nom de classe '{class_name}' n'est pas existe dans db")



def list_tasks_with_details():
        connection = db_connection
        cursor = connection.cursor()

        # prendre les donnes depuis table tasks
        cursor.execute("SELECT * FROM Tasks")
        tasks = cursor.fetchall()

        for task in tasks:
            task_id, week_number, student_id = task

            cursor.execute("SELECT firstname, lastname FROM students WHERE id = %s", (student_id,))
            student = cursor.fetchone()
            student_name, student_surname = student
            # convertion de date
            start_date = f"2023-01-01"
            # il calcule le date avec le fonction timedelta
            week_start = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(weeks=int(week_number) - 1)
            week_end = week_start + timedelta(days=4) # pour calcule last day

            print(
                f"ID: {task_id}, Student: {student_name} {student_surname}, Week: {week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')}")


        cursor.close()
        connection.close()

# delete student
def delete_student_from_tasks():
        firstname = input("prenom :")
        lastname = input("nom :")
        week_number = input("week_number :")

        connection = db_connection
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM Tasks WHERE student_id IN (SELECT id FROM students WHERE firstname = %s AND lastname = %s) AND week_number = %s",
            (firstname, lastname, week_number))

        if cursor.rowcount > 0:
            print(f"on a trouvé un eleve qu'il s'appelle {firstname} {lastname} et avec le numero de la semaine <{week_number}>.")
            confirmation = input(f"vous voulez supprimer cet eleve '{firstname} {lastname}' (y/n)\n")
            if confirmation == 'y':
                connection.commit()
                print(f"Vous avez supprime cet eleve '{firstname} {lastname}'!")
            else:
                print(f"vous avez annulé le transaction !")
        else:
            print("il n'existe pas.")

        cursor.close()
        connection.close()


# add student

def add_student_from_tasks():
    firstname = input("prenom :")
    lastname = input("nom :")

    connection = db_connection
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM students WHERE firstname = %s AND lastname = %s", (firstname, lastname))
    student_id = cursor.fetchone()

    if student_id:
        student_id = student_id[0]
        week_number = input("week number: ")

        cursor.execute("INSERT INTO Tasks (week_number, student_id) VALUES (%s, %s)", (week_number, student_id))

        if cursor.rowcount > 0:
            confirmation = input(f"vous voulez enregistrer cet eleve '{firstname} {lastname}' et avec le numero de la semaine <{week_number}> ? (y/n)\n")
            if confirmation == 'y':
                connection.commit()
                print(f"Vous avez ajouté cet eleve '{firstname} {lastname}'!")
            else:
                print(f"vous avez annulé le transaction !")
    else:
        print("cet eleve n'a pas pu trouvé.")


    cursor.close()
    connection.close()

def genererDocument():
    connection = db_connection
    cursor = connection.cursor()

    # prendre les donnes depuis table tasks
    cursor.execute("SELECT * FROM Tasks")
    tasks = cursor.fetchall()

    with open("Ordre_en_class.txt", "a", encoding="utf-8") as file:
        for task in tasks:
            task_id, week_number, student_id = task

            cursor.execute("SELECT firstname, lastname FROM students WHERE id = %s", (student_id,))
            student = cursor.fetchone()
            firstname, lastname = student
            # convertion de date
            start_date = f"2023-01-01"
            # il calcule le date avec le fonction timedelta
            week_start = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(weeks=int(week_number) - 1)
            week_end = week_start + timedelta(days=4)  # pour calcule last day

            file.write(f" Prenom: {firstname} Nom: {lastname} Week: {week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')}\n")
        print(f"enregistrer")

    cursor.close()
    connection.close()

