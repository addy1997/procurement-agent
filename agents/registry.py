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
            "role": "LAPTOP_FINDER",
            "capability": "Searching for suppliers in MongoDB, performing vector searches for specific categories, locations, and hardware specifications.",
            "class_name": "LaptopFinderAgent",
        },
        {
            "role": "COMPLIANCE_VALIDATOR",
            "capability": "Evaluating reliability scores, verifying vendor certifications, analyzing past performance notes for red flags, and conducting safety compliance checks.",
            "class_name": "ComplianceValidatorAgent",
        },
        {
            "role": "INVENTORY_ORCHESTRATOR",
            "capability": "Synchronizing stock levels across multiple internal ERP systems via HTTP/API calls.",
            "class_name": "InventoryOrchestratorAgent",
        },
        {
            "role": "CONTRACT_SUPERVISOR",
            "capability": "Managing negotiation workflows, RFQ scheduling, and contract lifecycle with shortlisted suppliers.",
            "class_name": "ContractSupervisorAgent",
        },
    ]

    for agent in agents:
        agent["capability_embedding"] = vo.embed(
            [agent["capability"]], model="voyage-3", input_type="document"
        ).embeddings[0]

    db.agents.delete_many({})
    db.agents.insert_many(agents)
    print("✅ Agent Registry seeded with vector embeddings.")


if __name__ == "__main__":
    seed_agent_registry()
