import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load variables from the .env in your root folder
load_dotenv()

def verify_atlas_connection():
    uri = os.getenv("MONGODB_URI")
    
    if not uri:
        print("❌ Error: MONGODB_URI not found in .env file.")
        return

    # Initialize MongoDB Client
    client = MongoClient(uri)

    try:
        # The ping command is the 'Hello World' of MongoDB
        client.admin.command('ping')
        print("✅ Connection Success: Your IP and Password are valid!")

        # Check if the database and collection exist or create them
        db = client.ProcureBot
        collection = db.suppliers
        
        # Test a simple write
        test_id = collection.insert_one({"status": "testing"}).inserted_id
        print(f"✅ Write Success: Document inserted with ID {test_id}")
        
        # Cleanup
        collection.delete_one({"_id": test_id})
        print("✅ Cleanup Success: Test document removed.")
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Ensure your IP is whitelisted in Atlas (Network Access).")
        print("2. Ensure your password in .env does NOT have < > brackets.")

if __name__ == "__main__":
    verify_atlas_connection()