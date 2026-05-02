import os
import voyageai
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
db = MongoClient(os.getenv("MONGODB_URI")).ProcureBot

def seed_agent_registry():
    agents = [
        {
            "role": "SOURCER",
            "capability": "Searching for suppliers in MongoDB, performing vector searches for specific categories, locations, and raw materials.",
            "class_name": "SourcerAgent"
        },
        {
            "role": "RISK_ANALYST",
            "capability": "Evaluating reliability scores, analyzing past performance notes for red flags, and conducting compliance checks.",
            "class_name": "RiskAnalystAgent"
        }
    ]

    for agent in agents:
        agent["capability_embedding"] = vo.embed(
            [agent["capability"]], 
            model="voyage-3", 
            input_type="document"
        ).embeddings[0]

    db.agents.insert_many(agents)
    print("✅ Agent Registry seeded with vector embeddings.")

if __name__ == "__main__":
    seed_agent_registry()