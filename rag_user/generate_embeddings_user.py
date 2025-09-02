from rag_model_users import initialize_rag_user

if __name__ == "__main__":
    # Cette fonction doit générer les embeddings et les stocker
    initialize_rag_user()
    print("Vector store généré et stocké avec succès.")