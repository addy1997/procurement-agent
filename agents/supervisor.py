import json
import time
import voyageai
from datetime import datetime
from groq import Groq
from pymongo import MongoClient

from config.config_manager import get_config
from agents.laptop_finder import LaptopFinderAgent
from agents.compliance_validator import ComplianceValidatorAgent


class ProcurementSupervisor:
    def __init__(self):
        self.groq_key = get_config("GROQ_API_KEY")
        self.voyage_key = get_config("VOYAGE_API_KEY")
        self.mongo_uri = get_config("MONGODB_URI")

        self.client = Groq(api_key=self.groq_key)
        self.vo = voyageai.Client(api_key=self.voyage_key)
        self.db = MongoClient(self.mongo_uri).ProcureBot

        self.laptop_finder = LaptopFinderAgent()
        self.compliance_validator = ComplianceValidatorAgent()
        self.model = "llama-3.3-70b-versatile"

    def run(self, user_query):
        def datetime_handler(obj):
            return obj.isoformat() if isinstance(obj, datetime) else str(obj)

        print("\n--- 🧠 Phase 1: Memory Retrieval ---")

        query_emb = self.vo.embed([user_query], model="voyage-3", input_type="query").embeddings[0]

        past_experience = list(self.db.experience.aggregate([
            {"$vectorSearch": {
                "index": "experience_vector_index",
                "path": "query_embedding",
                "queryVector": query_emb,
                "numCandidates": 5,
                "limit": 1,
            }},
            {"$addFields": {"score": {"$meta": "vectorSearchScore"}}},
        ]))

        if past_experience and past_experience[0].get("score", 0) > 0.92:
            print("✨ Found matching experience in memory!")
            return f"[MEMO: RECALLED FROM PREVIOUS TASK]\n{past_experience[0]['recommendation']}"

        # Voyage AI free tier = 3 RPM. Wait before the next embed call in LAPTOP_FINDER.
        print("⏳ Rate-limit cooldown (22s) before agent pipeline...")
        time.sleep(22)

        task_id = self.db.tasks.insert_one({
            "query": user_query,
            "status": "in_progress",
            "context_data": {},
            "history": [],
            "created_at": datetime.now(),
        }).inserted_id

        for step in range(5):
            current_state = self.db.tasks.find_one({"_id": task_id})
            ctx = current_state["context_data"]

            # Deterministic state-machine routing — avoids LLM hallucination on data_keys
            if "suppliers" not in ctx:
                next_step = "LAPTOP_FINDER"
            elif "compliance_report" not in ctx:
                next_step = "COMPLIANCE_VALIDATOR"
            else:
                next_step = "FINISH"

            print(f"🔀 Routing → {next_step}")

            if next_step == "FINISH":
                break

            # LAPTOP_FINDER calls Voyage AI on every run — always respect 3 RPM limit.
            # COMPLIANCE_VALIDATOR uses Groq only, so no cooldown needed there.
            if next_step == "LAPTOP_FINDER" and step > 0:
                print("⏳ Cooldown (22s)...")
                time.sleep(22)

            if next_step == "LAPTOP_FINDER":
                results = self.laptop_finder.execute_task(user_query)
                self.db.tasks.update_one({"_id": task_id}, {
                    "$set": {"context_data.suppliers": results},
                    "$push": {"history": "LAPTOP_FINDER_COMPLETED"},
                })
            elif next_step == "COMPLIANCE_VALIDATOR":
                suppliers = ctx.get("suppliers", [])
                report = self.compliance_validator.execute_task(suppliers)
                self.db.tasks.update_one({"_id": task_id}, {
                    "$set": {"context_data.compliance_report": report},
                    "$push": {"history": "COMPLIANCE_VALIDATOR_COMPLETED"},
                })

        final_state = self.db.tasks.find_one({"_id": task_id})
        final_context = json.dumps(final_state["context_data"], default=datetime_handler)

        final_res = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": f"Final Context: {final_context}\nProvide recommendation for: {user_query}"}],
        )

        recommendation = final_res.choices[0].message.content
        self.db.tasks.update_one({"_id": task_id}, {"$set": {"status": "completed"}})

        self.db.experience.insert_one({
            "query": user_query,
            "query_embedding": query_emb,
            "recommendation": recommendation,
            "created_at": datetime.now(),
        })

        return recommendation


def lambda_handler(event, context):
    query = event.get("query", "Find electronics suppliers in London")
    try:
        supervisor = ProcurementSupervisor()
        result = supervisor.run(query)
        return {"statusCode": 200, "body": json.dumps({"recommendation": result})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


if __name__ == "__main__":
    sup = ProcurementSupervisor()
    print(sup.run("Find me electronics suppliers in London and check their risk."))
