import os
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from dotenv import load_dotenv

# 🔐 Carica variabili da .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# 📚 Setup
app = FastAPI()
model = SentenceTransformer("all-mpnet-base-v2")
client = MongoClient(MONGO_URI)
db = client["unibg_tedx_2025"]
collection = db["tedx_data"]

# 📥 Schema input
class PromptRequest(BaseModel):
    text: str
    top_k: int = 1  # quanti risultati vuoi (default: 1)

# 🔍 Similarità coseno
def cosine_similarity(a, b):
    return np.dot(a, b)

# 🧠 API
@app.post("/match")
def match_prompt(request: PromptRequest):
    query_text = request.text.strip()
    top_k = request.top_k

    if not query_text:
        return {"error": "Prompt vuoto."}

    # 1. Embedding del prompt
    query_emb = model.encode(query_text)
    query_emb = query_emb / np.linalg.norm(query_emb)

    # 2. Recupero embedding video
    results = []
    for doc in collection.find({"embedding": {"$exists": True}}):
        video_emb = np.array(doc["embedding"])
        score = cosine_similarity(query_emb, video_emb)
        results.append({
            "id": str(doc["_id"]),
            "title": doc.get("title", "N/A"),
            "description": doc.get("description", ""),
            "score": float(score)
        })

    # 3. Ordina per similarità
    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "prompt": query_text,
        "results": results[:top_k]
    }
    