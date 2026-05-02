import json
import time
import voyageai
from datetime import datetime
from groq import Groq
from pymongo import MongoClient

# Custom modules
from config_manager import get_config
from sourcer_agent import SourcerAgent
from risk_analyst import RiskAnalystAgent

class ProcurementSupervisor:
    def __init__(self):
        # --- SECURE CONFIGURATION ---
        self.groq_key = get_config("GROQ_API_KEY")
        self.voyage_key = get_config("VOYAGE_API_KEY")
        self.mongo_uri = get_config("MONGODB_URI")

        # Initialize Clients
        self.client = Groq(api_key=self.groq_key)
        self.vo = voyageai.Client(api_key=self.voyage_key)
        self.db = MongoClient(self.mongo_uri).ProcureBot
        
        # Initialize Agents
        self.sourcer = SourcerAgent()
        self.risk_analyst = RiskAnalystAgent()
        self.model = "llama-3.3-70b-versatile"

    def run(self, user_query):
        def datetime_handler(obj):
            return obj.isoformat() if isinstance(obj, datetime) else str(obj)

        print(f"\n--- 🧠 Phase 1: Memory Retrieval ---")
        
        # 1. Check Long-Term Memory
        query_emb = self.vo.embed([user_query], model="voyage-3", input_type="query").embeddings[0]
        
        past_experience = list(self.db.experience.aggregate([
            {"$vectorSearch": {
                "index": "experience_vector_index", 
                "path": "query_embedding",
                "queryVector": query_emb,
                "numCandidates": 5,
                "limit": 1
            }},
            {"$addFields": {"score": {"$meta": "vectorSearchScore"}}}
        ]))

        if past_experience and past_experience[0].get('score', 0) > 0.92:
            print("✨ Found matching experience in memory!")
            return f"[MEMO: RECALLED FROM PREVIOUS TASK]\n{past_experience[0]['recommendation']}"

        # 2. INITIALIZE TASK
        task_id = self.db.tasks.insert_one({
            "query": user_query,
            "status": "in_progress",
            "context_data": {},
            "history": [],
            "created_at": datetime.now()
        }).inserted_id

        # 3. COLLABORATION LOOP
        for step in range(5):
            current_state = self.db.tasks.find_one({"_id": task_id})
            data_keys = list(current_state['context_data'].keys())
            
            decision_prompt = f"""
            Goal: {user_query}
            Current Data Keys Available: {data_keys}
            Rules:
            1. No 'suppliers' -> SOURCER.
            2. Have 'suppliers' but no 'risk_report' -> RISK_ANALYST.
            3. Both exist -> FINISH.
            Return JSON: {{"next_step": "ROLE_NAME", "reason": "why"}}
            """

            res = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are an Orchestrator."},
                          {"role": "user", "content": decision_prompt}],
                response_format={"type": "json_object"}
            )
            
            decision = json.loads(res.choices[0].message.content)
            next_step = decision["next_step"]

            if next_step == "FINISH": break

            if step > 0:
                print(f"⏳ Cooldown (22s)...")
                time.sleep(22)

            if next_step == "SOURCER":
                results = self.sourcer.execute_task(user_query)
                self.db.tasks.update_one({"_id": task_id}, {
                    "$set": {"context_data.suppliers": results},
                    "$push": {"history": "SOURCER_COMPLETED"}
                })
            elif next_step == "RISK_ANALYST":
                suppliers = current_state['context_data'].get('suppliers', [])
                report = self.risk_analyst.execute_task(suppliers)
                self.db.tasks.update_one({"_id": task_id}, {
                    "$set": {"context_data.risk_report": report},
                    "$push": {"history": "RISK_ANALYST_COMPLETED"}
                })

        # 4. FINAL SYNTHESIS
        final_state = self.db.tasks.find_one({"_id": task_id})
        final_context = json.dumps(final_state['context_data'], default=datetime_handler)

        final_res = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": f"Final Context: {final_context}\nProvide recommendation for: {user_query}"}]
        )
        
        recommendation = final_res.choices[0].message.content
        self.db.tasks.update_one({"_id": task_id}, {"$set": {"status": "completed"}})
        
        # Save to Memory
        self.db.experience.insert_one({
            "query": user_query,
            "query_embedding": query_emb,
            "recommendation": recommendation,
            "created_at": datetime.now()
        })

        return recommendation

# --- AWS LAMBDA ENTRY POINT (TOP LEVEL) ---
def lambda_handler(event, context):
    """
    Entry point for AWS Lambda. 
    Accepts: {"query": "Your search term"}
    """
    query = event.get("query", "Find electronics suppliers in London")
    
    try:
        supervisor = ProcurementSupervisor()
        result = supervisor.run(query)
        return {
            'statusCode': 200,
            'body': json.dumps({"recommendation": result})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }

if __name__ == "__main__":
    sup = ProcurementSupervisor()
    print(sup.run("Find me electronics suppliers in London and check their risk."))