VALID_ROLES = {"LAPTOP_FINDER", "COMPLIANCE_VALIDATOR", "INVENTORY_ORCHESTRATOR", "CONTRACT_SUPERVISOR", "FINISH"}


class TaskDelegator:
    """Decides which sub-agent should act next based on current task state."""

    def decide_next(self, goal: str, context: dict) -> dict:
        """Deterministic routing based on which keys are present in context."""
        if "suppliers" not in context:
            return {"next_step": "LAPTOP_FINDER", "reason": "No supplier data yet"}
        if "compliance_report" not in context:
            return {"next_step": "COMPLIANCE_VALIDATOR", "reason": "Suppliers found, awaiting compliance check"}
        if "inventory_status" not in context:
            return {"next_step": "INVENTORY_ORCHESTRATOR", "reason": "Compliance done, awaiting inventory sync"}
        if "contract_schedule" not in context:
            return {"next_step": "CONTRACT_SUPERVISOR", "reason": "All data gathered, initiating negotiation"}
        return {"next_step": "FINISH", "reason": "All pipeline stages complete"}
