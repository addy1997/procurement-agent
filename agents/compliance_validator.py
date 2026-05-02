import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class ComplianceValidatorAgent:
    """Verifies external vendor certifications and safety compliance data."""

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"

    def execute_task(self, supplier_list):
        if not supplier_list:
            return "No suppliers provided for compliance validation."

        print(f"⚖️ ComplianceValidator: Analyzing {len(supplier_list)} suppliers...")

        def datetime_handler(obj):
            return obj.isoformat() if isinstance(obj, datetime) else str(obj)

        supplier_data_str = json.dumps(supplier_list, indent=2, default=datetime_handler)

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
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content


if __name__ == "__main__":
    agent = ComplianceValidatorAgent()
    mock_data = [{"name": "Test Corp", "past_notes": "Late deliveries and failed audit.", "reliability_score": 2.1}]
    print(agent.execute_task(mock_data))
