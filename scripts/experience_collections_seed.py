from pymongo import MongoClient
from datetime import datetime
from config.config_manager import get_config

# Connect
mongo_uri = get_config("MONGODB_URI")
db = MongoClient(mongo_uri).ProcureBot

# Insert a dummy record to "spawn" the collection
db.experience.insert_one({
    "query": "Seed Data",
    "query_embedding": [0.0] * 1024, # Dummy vector
    "recommendation": "This is a seed to create the collection.",
    "created_at": datetime.now()
})

print("✅ 'experience' collection created. Refresh your MongoDB Atlas view now!")