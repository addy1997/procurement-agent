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

        task_id = self.db.tasks.insert_one({
            "query": user_query,
            "status": "in_progress",
            "context_data": {},
            "history": [],
            "created_at": datetime.now(),
        }).inserted_id

        for step in range(5):
            current_state = self.db.tasks.find_one({"_id": task_id})
            data_keys = list(current_state["context_data"].keys())

            decision_prompt = f"""
            Goal: {user_query}
            Current Data Keys Available: {data_keys}
            Rules:
            1. No 'suppliers' -> LAPTOP_FINDER.
            2. Have 'suppliers' but no 'compliance_report' -> COMPLIANCE_VALIDATOR.
            3. Both exist -> FINISH.
            Return JSON: {{"next_step": "ROLE_NAME", "reason": "why"}}
            """

            res = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Procurement Orchestrator."},
                    {"role": "user", "content": decision_prompt},
                ],
                response_format={"type": "json_object"},
            )

            decision = json.loads(res.choices[0].message.content)
            next_step = decision["next_step"]

            if next_step == "FINISH":
                break

            if step > 0:
                print("⏳ Cooldown (22s)...")
                time.sleep(22)

            if next_step == "LAPTOP_FINDER":
                results = self.laptop_finder.execute_task(user_query)
                self.db.tasks.update_one({"_id": task_id}, {
                    "$set": {"context_data.suppliers": results},
                    "$push": {"history": "LAPTOP_FINDER_COMPLETED"},
                })
            elif next_step == "COMPLIANCE_VALIDATOR":
                suppliers = current_state["context_data"].get("suppliers", [])
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
