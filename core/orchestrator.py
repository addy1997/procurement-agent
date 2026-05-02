from core.task_delegation import TaskDelegator
from core.error_handling import handle_agent_error


class MultiAgentOrchestrator:
    """Routes tasks to sub-agents in a feedback loop until the goal is reached."""

    def __init__(self, delegator: TaskDelegator, agents: dict, db, max_steps: int = 5):
        self.delegator = delegator
        self.agents = agents  # {"ROLE_NAME": agent_instance}
        self.db = db
        self.max_steps = max_steps

    def run(self, task_id, goal: str):
        for step in range(self.max_steps):
            state = self.db.tasks.find_one({"_id": task_id})
            data_keys = list(state["context_data"].keys())

            decision = self.delegator.decide_next(goal, data_keys)
            next_role = decision["next_step"]

            if next_role == "FINISH":
                print(f"✅ Orchestrator: Goal reached after {step} steps.")
                break

            agent = self.agents.get(next_role)
            if agent is None:
                print(f"⚠️ Orchestrator: No agent registered for role '{next_role}'. Stopping.")
                break

            try:
                result = agent.execute_task(goal)
                self.db.tasks.update_one({"_id": task_id}, {
                    "$set": {f"context_data.{next_role.lower()}": result},
                    "$push": {"history": f"{next_role}_COMPLETED"},
                })
            except Exception as exc:
                error_info = handle_agent_error(next_role, exc)
                self.db.tasks.update_one({"_id": task_id}, {
                    "$push": {"history": f"{next_role}_FAILED"},
                    "$set": {f"context_data.{next_role.lower()}_error": error_info},
                })
                break
