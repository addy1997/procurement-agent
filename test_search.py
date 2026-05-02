import os
import voyageai
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Setup
vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.ProcureBot

def vector_search_test(query_text):
    # 1. Turn your question into a vector
    # NOTE: We use input_type="query" for the question
    query_vector = vo.embed([query_text], model="voyage-3", input_type="query").embeddings[0]

    # 2. Ask MongoDB to find the closest match mathematically
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index", 
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 10,
                "limit": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "name": 1,
                "past_notes": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    results = list(db.suppliers.aggregate(pipeline))
    
    print(f"\n🙋 User Question: {query_text}")
    if results:
        res = results[0]
        print(f"🤖 Agent Result: {res['name']}")
        print(f"📝 Agent Logic: {res['past_notes']}")
        print(f"📏 Similarity Score: {round(res['score'], 4)}")
    else:
        print("❌ No matches. Ensure your Index Name is 'vector_index' in Atlas.")

if __name__ == "__main__":
    # Test 1: Finding by 'Meaning'
    vector_search_test("I need a reliable packaging supplier in the UK")
    
    # Test 2: Finding by 'Sustainability' 
    vector_search_test("Who has a great eco-friendly rating but might be slow in winter?")