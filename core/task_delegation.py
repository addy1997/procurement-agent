import json
from groq import Groq

VALID_ROLES = {"LAPTOP_FINDER", "COMPLIANCE_VALIDATOR", "INVENTORY_ORCHESTRATOR", "CONTRACT_SUPERVISOR", "FINISH"}


class TaskDelegator:
    """Decides which sub-agent should act next based on current task state."""

    def __init__(self, client: Groq, model: str):
        self.client = client
        self.model = model

    def decide_next(self, goal: str, data_keys: list) -> dict:
        prompt = f"""
        Goal: {goal}
        Data collected so far: {data_keys}
        Available roles: {sorted(VALID_ROLES)}
        Rules:
        1. No 'suppliers' -> LAPTOP_FINDER.
        2. Have 'suppliers' but no 'compliance_report' -> COMPLIANCE_VALIDATOR.
        3. Have 'compliance_report' but no 'inventory_status' -> INVENTORY_ORCHESTRATOR.
        4. All data present -> CONTRACT_SUPERVISOR or FINISH.
        Return JSON: {{"next_step": "ROLE_NAME", "reason": "why"}}
        """
        res = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a procurement orchestrator."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        decision = json.loads(res.choices[0].message.content)
        if decision.get("next_step") not in VALID_ROLES:
            decision["next_step"] = "FINISH"
        return decision
