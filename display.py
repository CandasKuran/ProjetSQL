from database import *




def afficher_menu():
    print('Menu:')
    print("1. Afficher l'ordre en class")
    print("2. Générer le planning « Ordre en classe »")
    print("3. Valider l’ordre en classe de la semaine")
    print("4. Supprimer un élève de la liste")
    print("5. Ajouter un élève de la liste")
    print("6. Générer le document « Ordre en classe »")
    print("7. Sortir du menu")


def menu():

    db = database.open_db()
    afficher_menu()
    while True:

        choix = input("Choisissez une option : ")

        if choix == '1':
            #                                             +
            list_tasks_with_details()

        elif choix == '2':
            classes = get_all_classes()
            for (id, name) in classes:
                print("{} - {}".format(id, name))
        elif choix == '3':
            #Valider l’ordre en classe de la semaine
            pass
        elif choix == '4':
            #Supprimer un élève de la liste               +
            delete_student_from_tasks()
        elif choix == '5':
            # add student
            add_student_from_tasks()
        elif choix == '6':
            #Générer le document « Ordre en classe »      +
            genererDocument()
        elif choix == '7':
            #                                             +
            print("au revoir")
            break
        else:
            print("option invalide.")



