import os
import requests
import chromadb
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 1) On pointe explicitement vers le même dossier que là où tu as généré tes embeddings la première fois
VECTOR_STORE_PATH = "C:\\Users\\moham\\RAG_SAGE\\rag_habilitation\\chroma_persistent_storage_habilitation_6"
# 2) On charge (ou crée) le client persistant
chroma_client = chromadb.PersistentClient(path=VECTOR_STORE_PATH)
collection = chroma_client.get_or_create_collection(name="habilitation_qa_collection_6")


# Répertoire de tes .txt
directory_path = "C:\\Users\\moham\\RAG_SAGE\\rag_habilitation\\documentation_sage_habilitation"




def initialize_rag():
    """
    Initialise la collection : si elle est déjà peuplée, on ne ré-indexe pas.
    Sinon, on lit les fichiers .txt, on les chunk et on ajoute leurs embeddings.
    """
    count = collection.count()
    if count > 0:
        logger.info(f"Vector store déjà peuplé ({count} documents). Pas de ré-indexation.")
        return


    logger.info("Vector store vide. Début de l’indexation des documents…")
    if not os.path.exists(directory_path):
        msg = f"Le répertoire {directory_path} n'existe pas"
        logger.error(msg)
        raise FileNotFoundError(msg)


    # Chargement des documents
    documents = load_documents(directory_path)
    if not documents:
        msg = "Aucun document .txt trouvé dans le répertoire"
        logger.error(msg)
        raise ValueError(msg)
    logger.info(f"Nombre de documents chargés : {len(documents)}")


    # Découpage en chunks
    chunked_documents = []
    for doc in documents:
        for i, chunk in enumerate(split_documents(doc["text"])):
            chunked_documents.append({
                "id": f"{doc['id']}_chunk{i+1}",
                "text": chunk
            })


    if not chunked_documents:
        msg = "Aucun chunk généré à partir des documents"
        logger.error(msg)
        raise ValueError(msg)


    # Génération des embeddings et indexation
    for chunk in chunked_documents:
        try:
            emb = generate_embedding(chunk["text"])
            collection.add(
                documents=[chunk["text"]],
                embeddings=[emb],
                ids=[chunk["id"]]
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation du chunk {chunk['id']}: {e}")


    logger.info(f"Indexation terminée. Total documents indexés : {collection.count()}")




def process_prompt(prompt: str) -> str:
    logger.info(f"Début du traitement du prompt : {prompt}")
    try:
        question_emb = generate_embedding(prompt)
        logger.info("Embedding du prompt généré")


        results = collection.query(query_embeddings=[question_emb], n_results=1)
        logger.info(f"Résultat brut de la requête ChromaDB : {results}")


        docs = results.get("documents", [])
        if not docs or not docs[0]:
            logger.warning("Aucun document trouvé pour ce prompt")
            return "Erreur: Aucun document pertinent trouvé dans la base de données."


        context = docs[0][0]
        logger.info(f"Contexte récupéré : {context}")


        # Prompt détaillé pour guider le modèle
        full_prompt = f'''
        Tu es un expert en paramétrage des habilitations dans Sage X3. Ton rôle est d'analyser une demande utilisateur
        et de la comparer à la documentation pour extraire le meilleur chunk afin de dégager les informations suivantes
        avec une grande précision :


        - **Code_profil**: code du profil fonction
        - **Fonction**: code de la fonction
        - **Type** : "regroupement" ou "site", s'il n'est pas mentionné dans la demande de l'utilisateur mettez la chaine vide "" comme valeur pour cette clé.
        - **Par** : Nom du regroupement ou du site, s'il n'est pas mentionné dans la demande de l'utilisateur mettez la chaine vide "" comme valeur pour cette clé.
        - **Accès** : "oui" ou "non", s'il n'est pas mentionné dans la demande de l'utilisateur mettez la chaine vide "" comme valeur pour cette clé.
        - **options_exist": c'est une chaine de caractère qui modélise tous les options existants qui appartiennent à
            la même fonction où chaque caractère de la chaine représente une option et les caractères sont concaténées pour construire un seul mot pas de virgules entre les caractères comme celui de l'exemple ci-dessous. il est mentionné toujours dans le chunk sous le nom de options existant.
        - **options_restric" : c'est une chaine de caractère qui modélise tous les options que l'utilisateur veut les
            restreindre depuis la chaine options_exist et ces options sont mentionnées dans la demande de l'utilisateur et les caractères sont concaténées pour construire un seul mot pas de virgules entre les caractères comme celui de l'exemple ci-dessous et ils fauts que ces caractéres appartiennent à options_exist, s'il n'appartiennet pas vous devez les supprmer de options_restric.
        Voici le contexte extrait de la documentation :


        """
        {context}
        """


        Voici la demande de l’utilisateur :


        """
        {prompt}
        """


        Suis ces étapes pour analyser la demande :


        1. **identifie le code profil** qui est toujours mentionné dans la demande de l’utilisateur.
        2. **Identifie la fonction** mentionnée ou implicite dans la demande de l’utilisateur, utilise sa petite description pour faire sortir son code deouis le chunk extracté.
        4. **Détermine les options existant** qui existent dans le chunk et qui appartiennent à la fonction en description.
        5. **Détermine les options à restreindre** que l’utilisateur veut restreindre (par exemple, "je ne veux pas C" ou "restreindre l'option création"), tu dois dégager que les options seulement mentionné par l'utilisateur dans sa demande, n'essaye pas de prédire. si aucune options n'est mentionné utilise chaine vide "" pour cette clé.
        6. **vérification et validation de options_restric", il faut que tous caractére dans options_restric doit eppartient à options_exist sinon vous devez le supprimer de options_restric et ne garder que les options qui appartiennent à la fois à options_restric et à options_exist.
        7. **Détecte le type** (regroupement ou site) et le **nom** associé dans la demande ou le contexte, même que pour tout les autres clés si la valeur de ce clé est abscente dans la demande de l'utilisateur vous devez mettre une chaine vide comme une valeur de cet clé.
        8. **Évalue l’accès** (oui ou non) basé sur la demande et le contexte.s'il n'est pas mentionné dans la demande de l'utilisateur mettez la chaine vide "" comme valeur pour cette clé.


        Ensuite, structure ta réponse sous forme de dictionnaire avec les clés "code_profil", "fonction", "type", "par", "acces", "options_exist" et "options_restric". Si une information est absente ou ambiguë, utilise une chaine vide "" comme valeur pour cette clé.
        ATTENTION: parfois l'utilisateur veut vous tromper il introduit des options qui ne sont pas présents car il ne sait pas quels sont les options spécifiques pour la fonction qu'il decrit c'est pour quoi c'est à vous de
        vérifier que les options tirées à partir du texte sont tous mentionnées dans le chunk sinon tu élimine l'option qui n'existe pas dans le chunk.
        **Exemple de sortie :**


        {{
            "code_profil": "code",
            "fonction": "code",
            "type": "site",
            "par": "Paris",
            "acces": "oui",
            "options_exist": "CMS"
            "options_restric" : "S"
        }}


        **Ta réponse doit être uniquement le dictionnaire, sans texte supplémentaire ,sans commentaires et si la valeur d'une clé n'est pas mentionné dans la demande de l'tilisateur ou il y'a une doute pour sa valeur alors vous devez mettre une chaine vide pour la valeur du clé correspondant.  **
        **n'ajoutez aucun commentaire au dictionnaire, il est strictement interdit d'ajouter un commentaire au dictionnaire ni à l'intérieur ni à l'extérieur,la réponse doit être strictement au format json .
        '''
        logger.info("Prompt complet construit")


        response = ollama_chat(full_prompt, model="mistral")
        logger.info(f"Réponse brute d'Ollama: {response}")


        if not response:
            logger.warning("Réponse vide reçue d'Ollama")
            return "Erreur: Réponse vide du modèle."


        return response.strip()


    except Exception as e:
        logger.error(f"Erreur dans process_prompt: {e}")
        return f"Erreur: {e}"




def load_documents(directory: str):
    logger.info(f"Chargement des documents depuis {directory}")
    docs = []
    for fname in os.listdir(directory):
        if fname.lower().endswith(".txt"):
            path = os.path.join(directory, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    docs.append({"id": fname, "text": f.read()})
            except Exception as e:
                logger.error(f"Impossible de lire {fname}: {e}")
    return docs




def split_documents(text: str):
    """
    Coupe chaque ligne non-vide en chunk séparé.
    """
    return [line.strip() for line in text.split("\n") if line.strip()]




def generate_embedding(text: str, model="nomic-embed-text"):
    url = "http://localhost:11434/api/embeddings"
    payload = {"model": model, "prompt": text}
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["embedding"]
    except requests.Timeout:
        logger.error("Timeout lors de la génération de l'embedding")
        raise
    except requests.RequestException as e:
        logger.error(f"Erreur Ollama embedding: {e}")
        raise




# (Optionnellement, tu peux supprimer ollama_chat si pas utilisé ailleurs)
def ollama_chat(prompt: str, model="mistral"):
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        logger.error(f"Erreur Ollama chat: {e}")
        raise
