from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from contextlib import asynccontextmanager
import sys, os

# 1) Ajout des répertoires où se trouvent les modules
sys.path.append(os.path.abspath("C:\\Users\\moham\\RAG_SAGE\\rag_habilitation"))
sys.path.append(os.path.abspath("C:\\Users\\moham\\RAG_SAGE\\rag_user"))
sys.path.append(os.path.abspath("C:\\Users\\moham\\RAG_SAGE\\selenium_automation"))

# 2) Imports 
from selenuim_habilitation import fill_fields
from selenuim_user import fill_user
# from selenuim_profil_fonction import fill_profil
from rag_model_habilitation import initialize_rag, process_prompt
from rag_model_users import  initialize_rag_user, process_prompt_user
import json

# 3) Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 4) Initialisation async du modèle
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initialisation du modèle RAG au démarrage…")
    try:
        await asyncio.wait_for(
            asyncio.gather(
                asyncio.to_thread(initialize_rag),
                asyncio.to_thread(initialize_rag_user)
            ),
            timeout=1800.0  # 30 minutes pour les deux
        )        
        logger.info("Les deux modèles RAG ont été initialisés avec succès")
    except asyncio.TimeoutError:
        logger.error("Timeout lors de l'initialisation du RAG")
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du RAG: {e}")
        raise
    yield
    logger.info("Arrêt de l'application")

# 5) Application FastAPI
app = FastAPI(lifespan=lifespan)

# 6) Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chemin du fichier des corrections
CORRECTIONS_FILE = "corrections.json"

# Fonction pour sauvegarder les corrections dans un fichier JSON
def save_correction(prompt, incorrect_response, correction):
    try:
        # Charger les corrections existantes si le fichier existe
        if os.path.exists(CORRECTIONS_FILE):
            with open(CORRECTIONS_FILE, "r") as f:
                corrections = json.load(f)
        else:
            corrections = []
        
        # Ajouter la nouvelle correction (sous forme de chaîne)
        corrections.append({
            "prompt": prompt,
            "incorrect_response": incorrect_response,
            "correction": correction  # Correction en chaîne
        })
        
        # Sauvegarder dans le fichier
        with open(CORRECTIONS_FILE, "w") as f:
            json.dump(corrections, f, indent=2)
        
        logger.info("Correction enregistrée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de la correction: {e}")
        raise


# 7) Endpoint général pour l'habilitation
@app.post("/generate-json")
async def assistant_endpoint(request: Request):
    logger.info("Requête reçue sur POST /generate-json")
    try:
        data = await request.json()
        prompt = data.get("prompt")
        if not prompt:
            logger.warning("Prompt manquant")
            return {"error": "Prompt is required"}

        logger.info(f"Traitement du prompt: {prompt}")
        answer = process_prompt(prompt)
        return {"result": answer}
    except Exception as e:
        logger.error(f"Erreur serveur: {e}")
        return {"error": str(e)}

# 8) Endpoint spécifique utilisateur
@app.post("/user-json")
async def user_endpoint(request: Request):
    logger.info("Requête reçue sur POST /user-json")
    try:
        data = await request.json()
        prompt = data.get("prompt")
        if not prompt:
            logger.warning("Prompt manquant (user)")
            return {"error": "Prompt is required"}

        logger.info(f"Traitement du prompt USER: {prompt}")
        answer = process_prompt_user(prompt)
        return {"result": answer}
    except Exception as e:
        logger.error(f"Erreur serveur USER: {e}")
        return {"error": str(e)}


@app.post("/submit-correction")
async def submit_correction(request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt")
        incorrect_response = data.get("incorrect_response")
        correction = data.get("correction")
        
        if not prompt or not incorrect_response or not correction:
            return {"error": "Champs requis manquants"}
        
        # Sauvegarder la correction (sous forme de chaîne)
        save_correction(prompt, incorrect_response, correction)
        
        return {"status": "Correction reçue et enregistrée avec succès"}
    except Exception as e:
        logger.error(f"Erreur dans submit_correction: {e}")
        return {"error": str(e)}



# --------------------9) Endpoint spécifique profil fonction
# @app.post("/profil-json")
# async def profil_endpoint(request: Request):
#     logger.info("Requête reçue sur POST /profil-json")
#     try:
#         data = await request.json()
#         prompt = data.get("prompt")
#         if not prompt:
#             logger.warning("Prompt manquant (profil)")
#             return {"error": "Prompt is required"}

#         logger.info(f"Traitement du prompt PROFIL: {prompt}")
#         answer = process_prompt(prompt)
#         return {"result": answer}
#     except Exception as e:
#         logger.error(f"Erreur serveur PROFIL: {e}")
#         return {"error": str(e)}

# 10) Validation générale via automatisation Selenium
@app.post("/validate")
async def validate_endpoint(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    logger.info(f"Validation reçue (habilitation): {payload}")
    background_tasks.add_task(fill_fields, payload)
    logger.info("Tâche Selenium HABILITATION planifiée")
    return {"status": "ok"}

# 11) Validation spécifique utilisateur
@app.post("/validate-user")
async def validate_user(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    logger.info(f"Validation reçue (user): {payload}")
    background_tasks.add_task(fill_user, payload)
    logger.info("Tâche Selenium USER planifiée")
    return {"status": "ok"}

# 12) Validation spécifique profil
# @app.post("/validate-profil")
# async def validate_profil(request: Request, background_tasks: BackgroundTasks):
#     payload = await request.json()
#     logger.info(f"Validation reçue (profil): {payload}")
#     background_tasks.add_task(fill_profil, payload)
#     logger.info("Tâche Selenium PROFIL planifiée")
#     return {"status": "ok"}

# 13) Root
@app.get("/")
def read_root():
    logger.info("Requête GET reçue sur /")
    return {"message": "API is running"}