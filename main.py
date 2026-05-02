import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_mongodb import MongoDBByteStore
from langgraph.graph import StateGraph, END

load_dotenv()

# --- CONFIGURATION ---
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client.ProcureBot

# --- AGENT TOOLS ---
def check_historical_reliability(supplier_name: str):
    """Search MongoDB Atlas for a supplier's past performance."""
    supplier = db.suppliers.find_one({"name": {"$regex": supplier_name, "$options": "i"}})
    if supplier:
        return f"Found {supplier_name}: Reliability Score {supplier.get('reliability_score')}/5. Notes: {supplier.get('past_notes')}"
    return "No historical data found for this supplier."

# --- LANGGRAPH STATE ---
# This tracks what the agents have discussed
class AgentState(dict):
    pass

def analyst_node(state):
    print("--- ANALYST AGENT: Checking Database ---")
    # Logic for calling LLM to check database would go here
    return {"messages": ["Analyst found that EcoPack is highly reliable."]}

def supervisor_node(state):
    print("--- SUPERVISOR: Coordinating ---")
    # Logic for deciding next steps
    return {"messages": ["Supervisor suggests moving to final negotiation."]}

# --- CONSTRUCT THE GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("analyst", analyst_node)
workflow.add_node("supervisor", supervisor_node)

workflow.set_entry_point("analyst")
workflow.add_edge("analyst", "supervisor")
workflow.add_edge("supervisor", END)

app = workflow.compile()

if __name__ == "__main__":
    print("🤖 Procure-Bot System Initialized.")
    # Example input to start the graph
    # app.invoke({"messages": ["Start search for packaging suppliers"]})