import os
import json
import time
from groq import Groq
import voyageai
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Clients
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
db = MongoClient(os.getenv("MONGODB_URI")).ProcureBot

def generate_synthetic_suppliers(count=10):
    """Uses Groq to generate clean JSON data for suppliers."""
    prompt = f"""
    Generate {count} unique procurement supplier profiles. 
    Return ONLY a JSON object with a key "suppliers" containing a list of objects.
    Keys: "name", "category", "reliability_score", "location", "past_notes", "sustainability_rating"
    
    Ensure "past_notes" is a descriptive string (at least 15 words) and NOT empty.
    """
    
    completion = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant", 
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(completion.choices[0].message.content)
    # Flexible extraction in case the key varies
    suppliers = data.get("suppliers", data if isinstance(data, list) else [])
    
    # Filter out any entries that missing the required notes field
    return [s for s in suppliers if s.get("past_notes") and str(s["past_notes"]).strip()]

def upload_in_batches(total_needed=100):
    batch_size = 10
    current_total = 0
    
    print(f"🚀 Generating {total_needed} suppliers...")
    
    while current_total < total_needed:
        try:
            batch = generate_synthetic_suppliers(batch_size)
            if not batch:
                continue

            # 1. Embed the 'past_notes' (The bottleneck)
            notes = [str(s['past_notes']) for s in batch]
            vectors = vo.embed(notes, model="voyage-3", input_type="document").embeddings
            
            # 2. Attach vectors
            for idx, supplier in enumerate(batch):
                supplier['embedding'] = vectors[idx]
            
            # 3. Insert to Atlas
            db.suppliers.insert_many(batch)
            current_total += len(batch)
            
            print(f"✅ Progress: {current_total}/{total_needed} uploaded.")
            
            # FIX: Sleep to satisfy Voyage AI's 3 RPM limit
            if current_total < total_needed:
                print("⏳ Respecting Voyage AI 3-RPM limit. Sleeping 22s...")
                time.sleep(22) 
            
        except Exception as e:
            print(f"⚠️ Batch error, retrying in 5s: {e}")
            time.sleep(5)

if __name__ == "__main__":
    upload_in_batches(50)