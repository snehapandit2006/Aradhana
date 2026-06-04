import os
import cohere
import chromadb
from typing import List

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")

# Initialize Chroma client
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection("astrology_knowledge")

def retrieve(query: str, top_k: int = 3) -> List[str]:
    """
    Embeds the user query using Cohere and retrieves the top_k closest documents from Chroma DB.
    """
    if not COHERE_API_KEY or COHERE_API_KEY == "your_cohere_api_key_here":
        # Fallback if API keys are missing, return empty or mock data to prevent crashes
        return []

    co = cohere.Client(api_key=COHERE_API_KEY)
    
    try:
        # Embed the query
        response = co.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        )
        query_embedding = response.embeddings[0]
        
        # Query Chroma DB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Extract document texts
        documents = results.get("documents", [[]])[0]
        return documents
        
    except Exception as e:
        print(f"Error in RAG retrieve: {e}")
        raise RuntimeError(f"Chroma/Cohere RAG retrieval failed: {str(e)}") from e
