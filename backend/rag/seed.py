import os
import json
import cohere
import chromadb
from dotenv import load_dotenv

# Load env variables if run as a script
load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_PATH = os.path.join(BACKEND_DIR, "chroma_db")
DATA_FILE_PATH = os.path.join(BACKEND_DIR, "data", "astrology_knowledge.jsonl")

def seed_database():
    """
    Seeds the Chroma DB with embedded chunks from astrology_knowledge.jsonl.
    """
    if not COHERE_API_KEY or COHERE_API_KEY == "your_cohere_api_key_here":
        print("Error: COHERE_API_KEY is not configured in the environment.")
        return

    if not os.path.exists(DATA_FILE_PATH):
        print(f"Error: Knowledge file not found at {DATA_FILE_PATH}")
        return

    # Initialize Chroma and Cohere
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = chroma_client.get_or_create_collection("astrology_knowledge")
    co = cohere.Client(api_key=COHERE_API_KEY)

    print("Reading knowledge base chunks...")
    chunks = []
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line.strip()))

    total_chunks = len(chunks)
    print(f"Loaded {total_chunks} chunks. Checking for existing entries in Chroma...")

    # Filter out already seeded chunks
    new_chunks = []
    for chunk in chunks:
        doc_id = chunk["id"]
        # Check if ID exists in collection
        res = collection.get(ids=[doc_id])
        if res and res["ids"]:
            print(f"Skipping {doc_id} (already seeded)")
        else:
            new_chunks.append(chunk)

    if not new_chunks:
        print("All chunks are already seeded. Database is up to date!")
        return

    print(f"Seeding {len(new_chunks)} new chunks...")
    
    # Process in batches to prevent API rate limit issues
    batch_size = 20
    for i in range(0, len(new_chunks), batch_size):
        batch = new_chunks[i:i + batch_size]
        
        texts = [item["text"] for item in batch]
        ids = [item["id"] for item in batch]
        metadatas = [{
            "category": item["category"],
            "topic": item["topic"],
            "tags": ",".join(item.get("tags", []))
        } for item in batch]

        try:
            print(f"Embedding batch {i // batch_size + 1}... ", end="", flush=True)
            response = co.embed(
                texts=texts,
                model="embed-english-v3.0",
                input_type="search_document"
            )
            embeddings = response.embeddings
            
            # Upsert into Chroma
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            print("done.")
            
        except Exception as e:
            print(f"\nFailed to seed batch: {e}")
            break

    print("Seeding process completed!")

if __name__ == "__main__":
    seed_database()
