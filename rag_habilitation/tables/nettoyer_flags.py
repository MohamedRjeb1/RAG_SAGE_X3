import pandas as pd
import ast

# Étape 1 : Lire le fichier CSV
df = pd.read_csv('rag_habilitation\\tables\\fonctions_avant_tout_nettoyage.csv', sep=';', encoding='utf-8')

# Étape 2 : Supprimer les lignes où "Désignation" est "#N/A" ou vide
df_cleaned = df[df['Désignation'].notna() & (df['Désignation'] != '#N/A')]

# Étape 3 : Créer un dictionnaire de flags avec leurs significations pour chaque ligne
def create_flag_dict(row):
    flag_dict = {}
    for i in range(13):  # De FLAG_0 à FLAG_12 et Texte0 à Texte12
        flag_col = f'FLAG_{i}'
        texte_col = f'Texte{i}'
        if pd.notna(row[flag_col]) and row[flag_col].strip() != '':
            flag = row[flag_col].strip()
            # Récupérer la signification ou "Signification inconnue" si absente
            signification = row[texte_col].strip() if pd.notna(row[texte_col]) else "Signification inconnue"
            flag_dict[flag] = signification
    return flag_dict

# Appliquer la fonction à chaque ligne
df_cleaned['flags'] = df_cleaned.apply(create_flag_dict, axis=1)

def add_extra_flags_if_type2(row):
    if row['TYP_0'] == 2:
        extra = {'C': 'Création', 'M': 'Modification', 'S': 'Suppression'}
        row['flags'].update(extra)
    return row



# Étape 4 : Sélectionner les colonnes pertinentes
df_flags = df_cleaned[['CODINT_0', 'flags', 'Désignation', 'TYP_0']]


def clean_flag_values(flag_dict_str):
    if isinstance(flag_dict_str, dict):
        flag_dict = flag_dict_str
    else:
        flag_dict = ast.literal_eval(flag_dict_str)
    cleaned_dict = {k: v[2:] if len(v) > 2 else '' for k, v in flag_dict.items()}
    return cleaned_dict

df_flags['flags'] = df_flags['flags'].apply(clean_flag_values)
df_flags = df_flags.apply(add_extra_flags_if_type2, axis=1)

# Ajouter la colonne 'options_exist'
df_flags['options_exist'] = df_flags['flags'].apply(lambda d: ''.join(d.keys()))

final_data=df_flags[['CODINT_0', 'flags', 'Désignation', 'options_exist']]

# Sauvegarder le résultat dans un nouveau fichier CSV
final_data.to_csv('cleaned_functions_avant_filtre.csv', index=False, sep=';', encoding='utf-8')






