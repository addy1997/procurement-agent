import logging

logger = logging.getLogger("procurebot")


class AgentError(Exception):
    def __init__(self, agent_name: str, message: str):
        self.agent_name = agent_name
        super().__init__(f"[{agent_name}] {message}")


def handle_agent_error(agent_name: str, exc: Exception) -> dict:
    logger.error(f"Agent '{agent_name}' failed: {exc}", exc_info=True)
    return {"agent": agent_name, "error": str(exc), "status": "failed"}
