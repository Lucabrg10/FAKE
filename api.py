import os
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId, errors
from openai import OpenAI

# 🔐 Carica variabili da .env
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 📚 Setup
app = FastAPI()
model = SentenceTransformer("all-mpnet-base-v2")
client = MongoClient(MONGO_URI)
db = client["unibg_tedx_2025"]
collection = db["tedx_data"]

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# 📥 Schema input
class PromptRequest(BaseModel):
    text: str
    top_k: int = 1

# 🔍 Similarità coseno
def cosine_similarity(a, b):
    return np.dot(a, b)

# 🎯 API di matching
@app.post("/match")
def match_prompt(request: PromptRequest):
    query_text = request.text.strip()
    top_k = request.top_k

    if not query_text:
        return {"error": "Prompt vuoto."}

    query_emb = model.encode(query_text)
    query_emb = query_emb / np.linalg.norm(query_emb)

    results = []
    for doc in collection.find({
        "embedding": {"$exists": True},
        "transcript": {
            "$exists": True,
            "$ne": None,
            "$type": "string"
        }
    }):

        video_emb = np.array(doc["embedding"])
        score = cosine_similarity(query_emb, video_emb)
        results.append({
            "id": str(doc["_id"]),
            "title": doc.get("title", "N/A"),
            "description": doc.get("description", ""),
            "score": float(score)
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "prompt": query_text,
        "results": results[:top_k]
    }

# 🧠 Fake news generator
@app.post("/fake-news")
def generate_fake_news(request: PromptRequest):
    query_text = request.text.strip()
    top_k = request.top_k

    match_response = match_prompt(request)
    if not match_response.get("results"):
        return {"error": "Nessun video trovato."}

    top_video = match_response["results"][0]
    video_id = top_video["id"]

    doc = collection.find_one({"_id": video_id})
    if not doc:
        return {"error": "Video non trovato nel database."}

    transcript = doc.get("transcript")
    if not transcript:
        return {"error": "Nessuna trascrizione trovata.","video": doc.get("title", "N/A")}

    prompt = (
        f"Usa la seguente trascrizione di un talk per creare una fake news credibile, "
        f"distorcendo leggermente o esagerando i contenuti della trascrizione, così da rendere la fake-news abbastanza veritiera. "
        f"La fake news deve essere breve (massimo 2 righe), contenere un titolo, ed essere coerente con l'argomento scelto dall'utente.\n\n"
        f"Non deve contenere caratteri speciali ma solo testo, la prima riga deve essere il titolo e a capo il testo della fake-news"
        f"Trascrizione del talk:\n{transcript}\n\n"
        f"Argomento scelto dall'utente: {query_text}"
    )

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
        )
        full_fake_news  = response.choices[0].message.content
    except Exception as e:
        return {"error": f"Errore chiamata OpenAI: {str(e)}"}
    # Splitta in titolo + testo: la prima riga è il titolo, le altre sono il contenuto
    lines = full_fake_news.split("\n")
    fake_news_title = lines[0].strip()
    fake_news_text = " ".join(line.strip() for line in lines[1:]).strip()

    return {
        "video_title": doc.get("title", "N/A"),
        "video_speaker": doc.get("speakers", "N/A"),
        "video_url": doc.get("url", "N/A"),
        "video_image": doc.get("imageUrl", "N/A"),  # Cambia nome campo se diverso
        "fake_news_title": fake_news_title,
        "fake_news_text": fake_news_text
    }