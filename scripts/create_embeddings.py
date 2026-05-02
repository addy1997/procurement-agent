import os
import voyageai
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Setup Clients
vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.ProcureBot

def update_suppliers_with_voyage():
    suppliers = list(db.suppliers.find())
    print(f"🔄 Processing {len(suppliers)} suppliers...")
    
    for s in suppliers:
        # We combine the name, location, and notes into one 'searchable' string
        text_to_embed = f"Supplier: {s['name']}. Location: {s['location']}. Notes: {s['past_notes']}"
        
        # 'input_type="document"' is crucial for storage
        result = vo.embed([text_to_embed], model="voyage-3", input_type="document")
        vector = result.embeddings[0]
        
        # Update the document in MongoDB with the new 'embedding' field
        db.suppliers.update_one(
            {"_id": s["_id"]}, 
            {"$set": {"embedding": vector}}
        )
        print(f"✅ Embedded: {s['name']}")

if __name__ == "__main__":
    update_suppliers_with_voyage()