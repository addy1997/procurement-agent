import json
from groq import Groq


class IntentAnalyzer:
    """Parses raw user queries into structured procurement intents using an LLM."""

    def __init__(self, client: Groq, model: str):
        self.client = client
        self.model = model

    def analyze(self, query: str) -> dict:
        prompt = f"""
        Parse this procurement request into a structured intent.
        Query: {query}
        Return JSON: {{"category": "...", "location": "...", "budget": "...", "urgency": "low|medium|high"}}
        """
        res = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a procurement intent parser."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(res.choices[0].message.content)
