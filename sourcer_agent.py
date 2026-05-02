import os
from pymongo import MongoClient
import voyageai
from dotenv import load_dotenv

load_dotenv()

class SourcerAgent:
    def __init__(self):
        # Clients
        self.vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
        self.db = MongoClient(os.getenv("MONGODB_URI")).ProcureBot
        
    def execute_task(self, task_description, limit=3):
        """
        Translates a task into a vector search and retrieves raw supplier data.
        """
        print(f"🔍 Sourcer: Searching for '{task_description}'...")
        
        # 1. Create embedding for the search query
        response = self.vo.embed(
            [task_description], 
            model="voyage-3", 
            input_type="query"
        )

        # Handle different SDK return types (hasattr check)
        if hasattr(response, 'embeddings'):
            query_vector = response.embeddings[0]
        else:
            query_vector = response[0]

        # 2. Perform Vector Search in MongoDB
        results = self.db.suppliers.aggregate([
            {
                "$vectorSearch": {
                    "index": "vector_index", # Your Atlas Vector Index name
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 50,
                    "limit": limit
                }
            },
            {
                "$project": {
                    "embedding": 0, # Optimization: don't pass heavy vectors to next agent
                    "_id": 0
                }
            }
        ])
        
        suppliers = list(results)
        print(f"✅ Sourcer: Found {len(suppliers)} matches.")
        return suppliers

if __name__ == "__main__":
    # Local test
    agent = SourcerAgent()
    print(agent.execute_task("Electronics in London"))