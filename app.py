import os
import requests
import chromadb
import json
import time

# 1. Charger les documents texte
directory_path = "./documentation_sage_x3"
def load_documents(directory_path):
    print(f"----Chargement des documents depuis {directory_path}-----")
    documents = []
    for file in os.listdir(directory_path):
        if file.endswith(".txt"):
            with open(os.path.join(directory_path, file), "r", encoding="utf-8") as f:
                documents.append({"id": file, "text": f.read()})
    return documents

# 2. Découper les documents en chunks

def split_documents(text, chunk_size=1000, chunk_overlap=20):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks

# 3. Générer les embeddings avec Ollama

def generate_embedding(text, model="nomic-embed-text"):
    url = "http://localhost:11434/api/embeddings"
    data = {"model": model, "prompt": text}
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()["embedding"]

# 4. Générer une réponse avec Ollama (Mistral)

def ollama_chat(prompt, model="mistral"):
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt, "stream": False}
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()["response"]

# 5. Pipeline principal

def main():
    # Charger et découper les documents
    directory_path = "./documentation_sage_x3"
    documents = load_documents(directory_path)
    print(f"Chargé {len(documents)} documents")

    chunked_documents = []
    for doc in documents:
        chunks = split_documents(doc["text"])
        for i, chunk in enumerate(chunks):
            chunked_documents.append({
                "id": f"{doc['id']}_chunk{i+1}",
                "text": chunk
            })
    print(f"Nombre total de chunks : {len(chunked_documents)}")

    # Initialiser ChromaDB
    chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
    collection = chroma_client.get_or_create_collection(name="document_qa_collection")

    # Indexer les chunks dans ChromaDB
    print("Indexation des chunks dans ChromaDB...")
    for chunk in chunked_documents:
        emb = generate_embedding(chunk["text"])
        collection.add(
            documents=[chunk["text"]],
            embeddings=[emb],
            ids=[chunk["id"]]
        )
    print("Indexation terminée.")

    # Prompt détaillé pour extraction JSON
    prompt_template = '''
Tu es un agent intelligent spécialisé dans l'extraction d'informations sur la gestion des utilisateurs dans le système ERP SAGE X3.

Je vais te fournir un texte en langage naturel qui décrit un ou plusieurs paramètres d'un utilisateur à créer dans SAGE X3.

 Ta tâche est de :
Lire et comprendre le texte.
Extraire uniquement les informations explicitement mentionnées.
Générer un fichier JSON structuré selon le format suivant (voir ci-dessous).
Ne jamais deviner ou compléter des informations absentes du texte.
 Structure attendue du JSON (exemple de modèle cible) :
{{
  "syracuse_user": {{
    "login": "exemple_login",
    "active": true,
    "password": "mot_de_passe",
    "require_password_change": true,
    "language": "Français",
    "email": "email@exemple.com",
    "group": "NOM_DU_GROUPE",
    "roles": ["NOM_DU_ROLE"]
  }},
  "x3_user": {{
    "code": "CODE_UTILISATEUR",
    "name": "Nom Prénom",
    "login": "exemple_login",
    "active": true,
    "x3_connection": true,
    "web_services": true,
    "menu_profile": "MENU_ASSOCIÉ",
    "functional_profile": "PROFIL_FONCTIONNEL",
    "site": "SITE",
    "access_code": "DROIT_ACCES"
  }},
  "permissions": {{
    "functions": [
      {{
        "fnc": "FONCTION",
        "module": "MODULE",
        "access": "Oui",
        "options": "C M V",
        "site": "NOM_SITE"
      }}
    ]
  }}
}}
Si un champ n'est pas mentionné dans le texte, ne l'ajoute pas dans le JSON.

 Exemple d'entrée (texte utilisateur) :
Créer un utilisateur appelé Marwen Sassi, login msassi, code MSASS, fonction GES_COMPTA, accès lecture/écriture sur le site SFAX, groupe COMPTA, profil fonctionnel COMPTA_USER.

 Exemple de sortie attendue (JSON à générer) :
{{
  "syracuse_user": {{
    "login": "msassi",
    "group": "COMPTA"
  }},
  "x3_user": {{
    "login": "msassi",
    "code": "MSASS",
    "functional_profile": "COMPTA_USER"
  }},
  "permissions": {{
    "functions": [
      {{
        "fnc": "GES_COMPTA",
        "access": "Oui",
        "options": "C M",
        "site": "SFAX"
      }}
    ]
  }}
}}
Tu dois maintenant me retourner uniquement le JSON final correspondant à chaque texte que je vais t'envoyer.
Respecte scrupuleusement la structure, et ne jamais inventer ou deviner un champ si le texte ne le précise pas.

Voici le texte à traiter :
"""
{context}

{question}
"""
Réponds uniquement avec le JSON final, sans aucun texte autour.
'''

    # Boucle de questions/réponses
    while True:
        question = input("\nPosez votre texte utilisateur SAGE X3 (ou tapez 'exit' pour quitter) : ")
        if question.lower() == "exit":
            break
        # Générer l'embedding de la question
        question_emb = generate_embedding(question)
        # Chercher les chunks les plus proches
        results = collection.query(query_embeddings=[question_emb], n_results=3)
        context = "\n".join(results["documents"][0])
        # Construire le prompt détaillé
        prompt = prompt_template.format(context=context, question=question)
        # Générer la réponse avec Ollama
        reponse = ollama_chat(prompt, model="mistral")
        print("\nRéponse JSON de l'assistant :\n", reponse)
        # Essayer de parser la réponse en JSON
        try:
            data = json.loads(reponse)
            print("\nRéponse structurée (Python) :\n", data)
        except Exception as e:
            print("Erreur lors du parsing JSON :", e)
        # Proposer d'ajouter la question/réponse à la base de données
        ajouter = input("\nAjouter cette question/réponse à la base de données ? (o/n) : ")
        if ajouter.lower() == "o":
            nouveau_texte = f"Question : {question}\nRéponse : {reponse}"
            emb = generate_embedding(nouveau_texte)
            new_id = f"ajout_{int(time.time())}"
            collection.add(
                documents=[nouveau_texte],
                embeddings=[emb],
                ids=[new_id]
            )
            print("Ajouté à la base de données !")

if __name__ == "__main__":
    main()
