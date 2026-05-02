import os
from groq import Groq
import voyageai
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class GroqChatClient:
    """Conversational RAG client backed by Groq LLM and MongoDB vector search."""

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        self.vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
        self.db = MongoClient(os.getenv("MONGODB_URI")).ProcureBot
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = model
        self._history: list[dict] = []

    def chat(self, user_query: str) -> str:
        query_vector = self.vo.embed([user_query], model="voyage-3", input_type="query").embeddings[0]

        context_suppliers = list(self.db.suppliers.aggregate([
            {"$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 10,
                "limit": 3,
            }},
            {"$project": {"_id": 0, "name": 1, "location": 1, "past_notes": 1, "reliability_score": 1}},
        ]))

        system_prompt = f"""You are 'ProcureBot'.
Context from Database: {context_suppliers}
Rules:
- Use the context to answer questions.
- Reference previous parts of the conversation if the user asks follow-up questions."""

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self._history)
        messages.append({"role": "user", "content": user_query})

        completion = self.groq.chat.completions.create(
            model=self.model, messages=messages, temperature=0.2
        )
        response_text = completion.choices[0].message.content

        self._history.append({"role": "user", "content": user_query})
        self._history.append({"role": "assistant", "content": response_text})
        if len(self._history) > 10:
            self._history = self._history[-10:]

        return response_text


# Module-level convenience function kept for backwards compatibility
_default_client: GroqChatClient | None = None


def procurement_agent(user_query: str) -> str:
    global _default_client
    if _default_client is None:
        _default_client = GroqChatClient()
    return _default_client.chat(user_query)


if __name__ == "__main__":
    print("⚡ ProcureBot with Memory is Live. (Type 'exit' to quit)")
    client = GroqChatClient()
    while True:
        query = input("\nYou: ")
        if query.lower() == "exit":
            break
        print(f"\nAI: {client.chat(query)}")
