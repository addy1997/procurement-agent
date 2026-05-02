import os
from pymongo import MongoClient
import voyageai
from dotenv import load_dotenv

load_dotenv()


class LaptopFinderAgent:
    """Discovers new suppliers matching laptop/hardware specifications via vector search."""

    def __init__(self):
        self.vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
        self.db = MongoClient(os.getenv("MONGODB_URI")).ProcureBot

    def execute_task(self, task_description, limit=3):
        print(f"🔍 LaptopFinder: Searching for '{task_description}'...")

        response = self.vo.embed([task_description], model="voyage-3", input_type="query")
        query_vector = response.embeddings[0] if hasattr(response, "embeddings") else response[0]

        results = self.db.suppliers.aggregate([
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 50,
                    "limit": limit,
                }
            },
            {"$project": {"embedding": 0, "_id": 0}},
        ])

        suppliers = list(results)
        print(f"✅ LaptopFinder: Found {len(suppliers)} matches.")
        return suppliers


if __name__ == "__main__":
    agent = LaptopFinderAgent()
    print(agent.execute_task("Electronics in London"))
