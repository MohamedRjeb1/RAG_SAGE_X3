import csv


# Chemin du fichier texte
chemin_fichier = "rag_habilitation/tables/fonctions_final.txt"

# Initialiser la liste
fonctions_final = []

# Ouvrir le fichier et lire ligne par ligne
with open(chemin_fichier, "r", encoding="utf-8") as fichier:
    for ligne in fichier:
        mot = ligne.strip()
        if mot:  # Vérifie que la ligne n'est pas vide
            fonctions_final.append(mot)





# Charger la liste des fonctions depuis le fichier texte
chemin_fonctions = "rag_habilitation/tables/fonctions_final.txt"
with open(chemin_fonctions, "r", encoding="utf-8") as f:
    fonctions_final = [ligne.strip() for ligne in f if ligne.strip()]

# Ouvrir le fichier CSV et filtrer les lignes
chemin_csv = "rag_habilitation/tables/cleaned_functions_avant_filtre.csv"
lignes_filtrees = []

with open(chemin_csv, "r", encoding="utf-8") as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    header = next(reader)  # Lire l'en-tête
    lignes_filtrees.append(header)
    for row in reader:
        if row and row[0] in fonctions_final:
            lignes_filtrees.append(row)

# Sauvegarder le résultat dans un nouveau fichier CSV
chemin_sortie = "rag_habilitation/tables/cleaned_functions_flags_filtered.csv"
with open(chemin_sortie, "w", encoding="utf-8", newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerows(lignes_filtrees)

print(f"{len(lignes_filtrees)-1} lignes gardées dans {chemin_sortie}")