import os
from groq import Groq
import voyageai
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Setup Clients
vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
client = MongoClient(os.getenv("MONGODB_URI"))
db = client.ProcureBot
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# NEW: This list will store our back-and-forth
chat_history = []

def procurement_agent(user_query):
    global chat_history
    
    # 1. RETRIEVAL (Same as before)
    query_vector = vo.embed([user_query], model="voyage-3", input_type="query").embeddings[0]
    
    pipeline = [
        {"$vectorSearch": {
            "index": "vector_index",
            "path": "embedding",
            "queryVector": query_vector,
            "numCandidates": 10,
            "limit": 3
        }},
        {"$project": {"_id": 0, "name": 1, "location": 1, "past_notes": 1, "reliability_score": 1}}
    ]
    
    context_suppliers = list(db.suppliers.aggregate(pipeline))
    
    # 2. BUILDING THE PROMPT WITH MEMORY
    system_prompt = f"""
    You are 'ProcureBot'. 
    Context from Database: {context_suppliers}
    
    Rules:
    - Use the context to answer questions.
    - Reference previous parts of the conversation if the user asks follow-up questions.
    """
    
    # We build the message list starting with the system prompt
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add the historical context (the "Memory")
    messages.extend(chat_history)
    
    # Add the current user question
    messages.append({"role": "user", "content": user_query})
    
    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.2
    )

    response_text = completion.choices[0].message.content
    
    # SAVE TO MEMORY: Update history with this exchange
    chat_history.append({"role": "user", "content": user_query})
    chat_history.append({"role": "assistant", "content": response_text})
    
    # Keep memory lean (optional: only remember last 10 exchanges)
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]

    return response_text

if __name__ == "__main__":
    print("⚡ ProcureBot with Memory is Live. (Type 'exit' to quit)")
    while True:
        query = input("\nYou: ")
        if query.lower() == 'exit': break
        print(f"\nAI: {procurement_agent(query)}")