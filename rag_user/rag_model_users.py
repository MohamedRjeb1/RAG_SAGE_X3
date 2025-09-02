import os
import requests
import chromadb
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

directory_path = "C:\\Users\\moham\\RAG_SAGE\\rag_user\\documentation_sage_user"
VECTOR_STORE_PATH = "C:\\Users\\moham\\RAG_SAGE\\rag_user\\chroma_persistent_storage_user_final"
chroma_client = chromadb.PersistentClient(path=VECTOR_STORE_PATH)
collection = chroma_client.get_or_create_collection(name="user_qa_collection_final")

def initialize_rag_user():
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

def process_prompt_user(prompt: str) -> str:
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
        Tu es un expert en création des utilisateurs dans Sage X3. Ton rôle est d'analyser une demande utilisateur
        et de la comparer à la documentation pour extraire le meilleur chunk afin de dégager les informations suivantes
        avec une grande précision :

        - **Code**: code du l'utilisateur
        - **Nom**: nom de l'utilisateur 
        - **Connexion_X3**: indiqué par l'utilisateur dans sa demande il prend la valeur "Oui" s'il est mentionné dans la demande sinon il prend la chaine vide "" comme valeur.
        - **Connexion_WS**: indiqué par l'utilisateur dans sa demande il prend la valeur "Oui" s'il est mentionné dans la demande sinon il prend la chaine vide "" comme valeur.
        - **Demandeur**: indiqué par l'utilisateur dans sa demande il prend la valeur "Oui" s'il est mentionné dans la demande sinon il prend la chaine vide "" comme valeur.
        - **ctr_annuaire**: indiqué par l'utilisateur dans sa demande il prend la valeur "Oui" s'il est mentionné dans la demande sinon il prend la chaine vide "" comme valeur.
        - **mail**: indiqué par l'utilisateur dans sa demande, s'il n'est pas mentionné dans la demande, il prend la chaine vide comme valeur.
        - **telephone** : indiqué par l'utilisateur dans sa demande, s'il n'est pas mentionné dans la demande, il prend la chaine vide comme valeur.
        - **fax** : indiqué par l'utilisateur dans sa demande, s'il n'est pas mentionné dans la demande, il prend la chaine vide comme valeur.
        - **accès** : indiqué par l'utilisateur dans sa demande, s'il n'est pas mentionné dans la demande, il prend la chaine vide comme valeur.
        - **identif**: indiqué par l'utilisateur dans sa demande, s'il n'est pas mentionné dans la demande, il prend la chaine vide comme valeur.
        - **cod_metier** : indiqué par l'utilisateur dans sa demande, s'il n'est pas mentionné dans la demande, il prend la chaine vide comme valeur.
        - **Profil-menu** : indiqué par l'utilisateur dans sa demande, s'il n'est pas mentionné dans la demande, il prend la chaine vide comme valeur.
        - **Profil_fonction** : indiqué par l'utilisateur dans sa demande, s'il n'est pas mentionné dans la demande, il prend la chaine vide comme valeur.

        Voici le contexte extrait de la documentation :

        """
        {context}
        """

        Voici la demande de l’utilisateur :

        """
        {prompt}
        """

        Suis ces étapes pour analyser la demande mais n'affichez pas comment tu as suis ces étapes.donnez moi juste la réponse sous format json:

        1. **identifie les champs ** mentionnés ou implicites dans la demande de l'utilisateuret les mettre dans une liste champs_exist. 
        2. **identifie les champs ** non mentionnés ou non indiqués dans la demande de l’utilisateur et les mettre dans une liste champs_non_exist.
        3. **attribuer la chaine vide ** comme valeur pour tout les elements de la liste champs_non_exist.
        4. **attribuer les valeurs extractées ** qui existent dans la demande de l'utilisateur à chaque element de la liste champs_exist.
        5. **écrire le dictionnaire des informations complet**avec tous les elements des listes champs_exist et champs_non_exist et leurs valeurs correspondant.
        7. **nettoyage du dictionnaire**Ta réponse doit être uniquement le dictionnaire, sans texte supplémentaire ,sans commentaires et si la valeur d'une clé n'est pas mentionné dans la
          demande de l'tilisateur ou il y'a une doute pour sa valeur alors vous devez mettre une chaine vide pour la valeur du clé correspondant, n'ajoutez aucun commentaire au dictionnaire, il est strictement interdit d'ajouter un commentaire au dictionnaire ni à l'intérieur ni à l'extérieur.   
        

        Ensuite, structure ta réponse sous forme de dictionnaire avec les clés "code", "Nom", "actif", "Connexion_X3", "Connexion_WS",
        "Demandeur", "ctr_annuaire", "mail", "telephone", "fax", "accès", "identif", "fonction", "cod_metier", "Profil_menu",
        "Profil_fonction". Si une information est absente ou ambiguë, utilise une chaine vide "" comme valeur pour cette clé.
        ATTENTION: parfois l'utilisateur veut vous tromper il introduit des options qui ne sont pas présents car il ne sait pas quels sont les options spécifiques pour la fonction qu'il decrit c'est pour quoi c'est à vous de 
        vérifier que les options tirées à partir du texte sont tous mentionnées dans le chunk sinon tu élimine la valeur que son champ n'existe pas dans le chunk.
        **Exemple de sortie qui doit être uniquement le dictionnaire finale sans aucune phrase qui accompagne le dictionnaire, sans texte supplémentaire ,sans commentaires et si la valeur d'une clé n'est pas mentionné dans 
        la demande de l'tilisateur ou il y'a une doute pour sa valeur alors vous devez mettre une chaine vide pour la valeur du clé correspondant, n'ajoutez aucun
        commentaire au dictionnaire, il est strictement interdit d'ajouter un commentaire au dictionnaire ni à l'intérieur ni à l'extérieur, tu dois générer seulement le dictionnaire en format json je veux pas d'autres phrases
        qui lui accompagne, je veux qu'à la fin la réponse brute doit être seulement le dictionnaire finale au format json, c'est à dire ne précédez et ne suivez le dictionnaire finale par aucune phrase. je veux que la réponse doit être tout court le dictionnaire finale au format json.
        Ne dites pas "Voici la réponse en format dictionnaire ", je veux le dictionnaire tout court.
        je veux que la reponse finale ne doit pas etre une chaine, elle doit etre dictionnaire en json format sans aucune autre mot à l'exterieur du dictionnaire.
        n'ajoutez aucune phrase avant le dictionnaire pour introduire le dictionnaire finale, donnez le dictionnaire seulement. la réponse doit debuter par "```" qui indique le format json. 
        {{
            "code": "code de l'utilisateur",
            "Nom": "nom de l'utilisateur",
            "actif": "oui" ou "",
            "Connexion_X3":"oui" ou "",
            "Connexion_WS": "oui" ou "",
            "Demandeur": "oui" ou "",
            "ctr_annuaire" : "oui" ou "",
            "mail": "adresse mail de l'utilisateur" ou "",
            "telephone": "numéro de télèphone de l'utilisateur" ou "",
            "fax": "numéro de fax de l'utilisateur" ou "",
            "accès": "code de l'accès",
            "identif": "code de l'identifiant",
            "fonction": "nom de la fonction" ou "",
            "cod_metier" : "code du mètier" ou "",
            "Profil_menu": "nom du profil menu" ou "",
            "Profil_fonction" : "nom du profil fonction" ou ""
        }}
    
        Notez bien que tu doit générez seulement la sortie finale qui doit être seulement le dictionnaire finale qui est remplit n'affichez ni le processus de remplissage du dictionnaire ni la liste des champs qui sont mentionnés dans la demande de l'utilisateur et leur valeur correspondante , je veux que tu génére seulemt le dictionnaire finale .
             '''
        logger.info("Prompt complet construit")

        response = ollama_chat(full_prompt, model="mistral")
        logger.info(f"Réponse brute d'Ollama: {response}")

        if not response:
            logger.warning("Réponse vide reçue d'Ollama")
            return "Erreur: Réponse vide du modèle."

        return response.strip()

    except Exception as e:
        logger.error(f"Erreur dans process_prompt_user: {e}")
        return f"Erreur: {e}"

def load_documents(directory_path):
    logger.info(f"Chargement des documents depuis {directory_path}")
    documents = []
    for file in os.listdir(directory_path):
        if file.endswith(".txt"):
            try:
                with open(os.path.join(directory_path, file), "r", encoding="utf-8") as f:
                    documents.append({"id": file, "text": f.read()})
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier {file}: {str(e)}")
    return documents

def split_documents(text, chunk_size=1100, chunk_overlap=120):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks

def generate_embedding(text, model="nomic-embed-text"):
    url = "http://localhost:11434/api/embeddings"
    data = {"model": model, "prompt": text}
    try:
        response = requests.post(url, json=data, timeout=300)
        response.raise_for_status()
        return response.json()["embedding"]
    except requests.Timeout:
        logger.error("Timeout lors de la génération de l'embedding")
        raise Exception("Timeout lors de la génération de l'embedding")
    except requests.RequestException as e:
        logger.error(f"Erreur lors de la requête à Ollama pour embedding: {str(e)}")
        raise Exception(f"Erreur Ollama: {str(e)}")

def ollama_chat(prompt, model="mistral"):
    url = "http://localhost:11434/api/generate"
    data = {"model": model, "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=data, timeout=300)
        response.raise_for_status()
        return response.json()["response"]
    except requests.Timeout:
        logger.error("Timeout lors de la génération de la réponse")
        raise Exception("Timeout lors de la génération de la réponse")
    except requests.RequestException as e:
        logger.error(f"Erreur lors de la requête à Ollama pour réponse: {str(e)}")
        raise Exception(f"Erreur Ollama: {str(e)}")