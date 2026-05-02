import os
from groq import Groq
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

class RiskAnalystAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile" # Higher reasoning for risk

    def execute_task(self, supplier_list):
        if not supplier_list:
            return "No suppliers provided for analysis."

        print(f"⚖️ Risk Analyst: Analyzing {len(supplier_list)} suppliers...")

        # FIX: Define a helper to handle date serialization
        def datetime_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)

        # Apply the helper in json.dumps
        supplier_data_str = json.dumps(
            supplier_list, 
            indent=2, 
            default=datetime_handler # This handles the 'datetime' error
        )

        prompt = f"""
        Analyze the following supplier data for procurement risks. 
        Focus on reliability scores, sustainability, and any red flags in the 'past_notes'.
        
        Suppliers: {supplier_data_str}
        
        Return a summary for each supplier emphasizing Risk Level and a Recommendation.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a Senior Risk Compliance Officer."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content
        
if __name__ == "__main__":
    # Local test with mock data
    agent = RiskAnalystAgent()
    mock_data = [{"name": "Test Corp", "past_notes": "Late deliveries and failed audit.", "reliability_score": 2.1}]
    print(agent.execute_task(mock_data))