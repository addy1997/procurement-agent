import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def seed_suppliers():
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client.ProcureBot
    collection = db.suppliers

    sample_data = [
        {
            "name": "EcoPack Solutions",
            "category": "Packaging",
            "reliability_score": 4.9,
            "location": "London, UK",
            "past_notes": "Extremely reliable for sustainable cardboard. Always hits deadlines.",
            "sustainability_rating": "A+",
            "last_audit": datetime(2025, 12, 1)
        },
        {
            "name": "BioPlastic Corp",
            "category": "Packaging",
            "reliability_score": 3.2,
            "location": "Berlin, Germany",
            "past_notes": "High quality but frequent shipping delays in winter months.",
            "sustainability_rating": "B",
            "last_audit": datetime(2026, 1, 15)
        },
        {
            "name": "GreenStream Logistics",
            "category": "Shipping",
            "reliability_score": 4.5,
            "location": "London, UK",
            "past_notes": "Electric fleet used for all inner-city deliveries. Premium pricing.",
            "sustainability_rating": "A",
            "last_audit": datetime(2026, 2, 20)
        }
    ]

    try:
        # Clear existing test data and insert fresh records
        collection.delete_many({}) 
        result = collection.insert_many(sample_data)
        print(f"✅ Successfully seeded {len(result.inserted_ids)} suppliers into Atlas!")
    except Exception as e:
        print(f"❌ Seeding failed: {e}")

if __name__ == "__main__":
    seed_suppliers()