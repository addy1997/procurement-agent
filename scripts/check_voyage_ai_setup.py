import os
import voyageai
from dotenv import load_dotenv

load_dotenv()

# This uses the key you just generated
vo = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

try:
    # We use voyage-3 because it's their newest, most powerful model
    result = vo.embed(["Testing my new secret key"], model="voyage-3", input_type="document")
    print(f"✅ Success! Generated a vector with {len(result.embeddings[0])} dimensions.")
except Exception as e:
    print(f"❌ Connection Failed: {e}")