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
        task_id, week_number, student_id, validated = task  # inclure le champ validated ici

        cursor.execute("SELECT firstname, lastname FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        student_name, student_surname = student
        # convertion de date
        start_date = f"2023-01-01"
        # il calcule le date avec le fonction timedelta
        week_start = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(weeks=int(week_number) - 1)
        week_end = week_start + timedelta(days=4)  # pour calcule last day

        # Ajouter l'information validated dans la sortie
        validated_text = "Validated" if validated else "Not Validated"

        print(
            f"ID: {task_id}, Student: {student_name} {student_surname}, Week: {week_start.strftime('%Y/%m/%d')} - {week_end.strftime('%Y/%m/%d')} (Week {week_number}), Status: {validated_text}")



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




def genererDocument():
    connection = db_connection
    cursor = connection.cursor()

    # prendre les donnes depuis table tasks
    cursor.execute("SELECT * FROM Tasks")
    tasks = cursor.fetchall()

    with open("Ordre_en_class.csv", 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';')
        csv_writer.writerow(["prenom", "nom", "week", "validated"])
        for task in tasks:
            task_id, week_number, student_id, validated_value = task

            # Validate kolonunun değerini kontrol ediyoruz.
            validated = "Valide" if validated_value == 1 else "Non valide"

            cursor.execute("SELECT firstname, lastname FROM students WHERE id = %s", (student_id,))
            student = cursor.fetchone()
            firstname, lastname = student

            # convertion de date
            start_date = "2023-01-01"
            # il calcule le date avec le fonction timedelta
            week_start = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(weeks=int(week_number) - 1)
            week_end = week_start + timedelta(days=4)  # pour calcule last day

            csv_writer.writerow([firstname, lastname, f"{week_start.strftime('%Y/%m/%d')}-{week_end.strftime('%Y/%m/%d')}", validated])
        print("enregistrer")



# les fonctions pour generer le planing order en classe
# get students, get_planings_for_class,add_or_update_planning,generer_planning_ordre_en_classe
def get_students_from_class(class_name):
    query = "SELECT id,firstname, lastname FROM students WHERE class_id = (SELECT id FROM classes WHERE name = %s) ORDER BY firstname, lastname"
    cursor = db_connection.cursor()
    cursor.execute(query, (class_name,))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_planning_for_class(class_name, start_date, end_date):
    query = """SELECT week_number, student_id FROM tasks 
              WHERE student_id IN (SELECT id FROM students WHERE class_id = (SELECT id FROM classes WHERE name = %s)) 
              AND week_number BETWEEN %s AND %s ORDER BY week_number"""
    cursor = db_connection.cursor()
    cursor.execute(query, (class_name, start_date, end_date))
    rows = cursor.fetchall()
    cursor.close()
    return rows


def add_or_update_planning(week_number, student_id):
    # Check si le planing existe pour cet semaine
    query_check = "SELECT id FROM tasks WHERE week_number = %s AND student_id = %s"
    cursor = db_connection.cursor()
    cursor.execute(query_check, (week_number, student_id))
    existing_entry = cursor.fetchone()

    if existing_entry:
        # Update planning
        query_update = "UPDATE tasks SET student_id = %s WHERE week_number = %s"
        cursor.execute(query_update, (student_id, week_number))
    else:
        # ajouter nouveau planing
        query_insert = "INSERT INTO tasks (week_number, student_id) VALUES (%s, %s)"
        cursor.execute(query_insert, (week_number, student_id))

    cursor.close()

def generer_planning_ordre_en_classe():
    nom_classe = input("Entrez le nom de la classe: ")
    date_debut = int(input("Entrez la semaine de début (e.g. 1, 2, ...): "))
    date_fin = int(input("Entrez la semaine de fin: "))

    existing_planning = get_planning_for_class(nom_classe, date_debut, date_fin)

    eleves = get_students_from_class(nom_classe)

    if existing_planning:
        latest_week = existing_planning[-1][0]  # pour return planing by week_number
        next_week_to_plan = latest_week + 1
    else:
        next_week_to_plan = date_debut

    eleve_index = 0
    for week in range(next_week_to_plan, date_fin + 1):
        student_id = eleves[eleve_index][0]
        add_or_update_planning(week, student_id)

        eleve_index += 1
        if eleve_index >= len(eleves):
            eleve_index = 0

    print("Planning généré avec succès!")









# valider class order
def validate_class_order():
    # 1. Demandez le nom de la classe
    class_name = input("Entrez le nom de la classe pour laquelle l'ordre doit être validé: ")

    class_id = classnameID().get(class_name, None)
    if not class_id:
        print("Classe non trouvée!")
        return

    # 2. Demandez la date
    today = datetime.today().date()
    date_str = input(f"Entrez la date pour laquelle l'ordre en classe est validé (par défaut {today}): ")
    if not date_str:
        date_str = today
    else:
        date_str = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Calculer le numéro de la semaine
    start_date = datetime.strptime("2023-01-01", "%Y-%m-%d").date()
    week_number = (date_str - start_date).days // 7 + 1

    # Trouver l'élève responsable de cette semaine
    cursor = db_connection.cursor()
    cursor.execute("SELECT student_id FROM Tasks WHERE week_number = %s", (week_number,))
    student_id = cursor.fetchone()[0]
    student_name = get_student(student_id)
    if not student_name:
        print("Pas d'élève trouvé pour cette semaine!")
        return

    # 3. Proposer le nom de l'élève
    response = input(f"{student_name[1]} {student_name[0]} a-t-il effectué le nettoyage? (y/n): ")
    if response == 'n':
        new_student_name = input("Entrez le prenom de l'élève qui a effectué le nettoyage: ")
        new_student_surname = input("Entrez le nom de l'élève qui a effectué le nettoyage: ")

        cursor.execute("SELECT id FROM students WHERE firstname = %s AND lastname = %s",
                       (new_student_name, new_student_surname))
        new_student_data = cursor.fetchone()

        if new_student_data:
            new_student_id = new_student_data[0]
            cursor.execute("UPDATE Tasks SET student_id = %s WHERE week_number = %s", (new_student_id, week_number))
            print(
                f"{new_student_name} {new_student_surname} est maintenant responsable de l'ordre pour la semaine {week_number}.")
        else:
            print("L'élève entré n'a pas été trouvé dans la base de données.")
            return

    # 5. Mettre à jour le champ booléen (à supposer que ce champ s'appelle `validated`)
    cursor.execute("UPDATE Tasks SET validated = TRUE WHERE week_number = %s", (week_number,))
    print(f"L'ordre en classe pour la semaine {week_number} a été validé!")

    cursor.close()

#------------------------test ------------------






