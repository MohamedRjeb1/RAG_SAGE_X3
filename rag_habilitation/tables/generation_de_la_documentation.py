import pandas as pd

df_flags = pd.read_csv('rag_habilitation/tables/cleaned_functions_apres_filtre.csv', sep=';', encoding='utf-8')

code = df_flags['CODINT_0']

flags = df_flags['flags']


designation = df_flags['Désignation']

options_existants= df_flags['options_exist']


l = [[code[i], flags[i], designation[i], str(options_existants[i])] for i in range(len(code))]



with open("rag_habilitation/documentation_sage_habilitation/habilitation_qa_collection.txt", "w", encoding="utf-8") as f:
    for i in range(len(l)):
        f.write("la fonction ayant le code "+ l[i][0]+" est une fonction utilisée pour "+ l[i][2]+" et ses options sont : "+ l[i][1]+" et sa liste options_exist correspondante est "+l[i][3]+"."+"\n")








