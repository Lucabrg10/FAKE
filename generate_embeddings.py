import os
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["unibg_tedx_2025"]
collection = db["tedx_data"]

model = SentenceTransformer("all-mpnet-base-v2")

documents = list(collection.find({}))

for doc in tqdm(documents):
    desc = doc.get("description")
    if not desc:
        continue

    new_embedding = model.encode(desc)
    new_embedding = new_embedding / np.linalg.norm(new_embedding)

    current_embedding = doc.get("embedding")

    update_needed = False

    if current_embedding is None:
        update_needed = True
    else:
        current_embedding = np.array(current_embedding)

        # ⚠️ Check dimensione
        if current_embedding.shape != new_embedding.shape:
            update_needed = True
        elif not np.allclose(new_embedding, current_embedding):
            update_needed = True

    if update_needed:
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"embedding": new_embedding.tolist()}}
        )
        print(f"✅ Aggiornato: {doc['_id']} — nuova shape: {new_embedding.shape}")
    else:
        print(f"⏭️ Già aggiornato: {doc['_id']}")

print("🎉 Embedding aggiornati dove necessario!")
