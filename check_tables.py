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

print(f"Checking Supabase tables...")
print(f"URL: {SUPABASE_URL}")

# Check what tables exist
try:
    # Try to get table information
    res = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
    print(f"Tables endpoint status: {res.status_code}")
    print(f"Tables response: {res.text}")
except Exception as e:
    print(f"Error checking tables: {e}")

# Try to create the chat_history table
print("\n=== Creating chat_history table ===")
create_table_sql = """
CREATE TABLE IF NOT EXISTS chat_history (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

try:
    # Note: This might not work with the REST API, you may need to use the SQL editor in Supabase dashboard
    print("Please create the table manually in your Supabase dashboard with this SQL:")
    print(create_table_sql)
except Exception as e:
    print(f"Error: {e}")

print("\n=== Manual Steps Required ===")
print("1. Go to your Supabase dashboard")
print("2. Go to SQL Editor")
print("3. Run this SQL:")
print(create_table_sql)
print("4. Then test the endpoints again") 