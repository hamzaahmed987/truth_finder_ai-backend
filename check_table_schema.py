import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print(f"Checking chat_history table schema...")
print(f"URL: {SUPABASE_URL}")

# Try to get table schema information
try:
    # Get table info from Supabase REST API
    res = requests.get(f"{SUPABASE_URL}/rest/v1/chat_history?limit=1", headers=headers)
    print(f"Table info status: {res.status_code}")
    print(f"Table info response: {res.text}")
    
    # Try to get schema info
    schema_res = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
    print(f"\nSchema info status: {schema_res.status_code}")
    if schema_res.status_code == 200:
        schema_data = schema_res.json()
        if 'paths' in schema_data and '/chat_history' in schema_data['paths']:
            chat_history_info = schema_data['paths']['/chat_history']
            print(f"Chat history table info: {chat_history_info}")
        else:
            print("No chat_history table found in schema")
    
except Exception as e:
    print(f"Error checking schema: {e}")

print("\n=== Manual Steps ===")
print("1. Go to your Supabase dashboard")
print("2. Go to Table Editor")
print("3. Click on the 'chat_history' table")
print("4. Tell me what columns you see")
print("5. Or run this SQL to see the schema:")
print("   SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'chat_history';") 