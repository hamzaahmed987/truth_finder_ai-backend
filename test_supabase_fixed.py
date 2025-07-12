import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

print(f"Testing Supabase with correct column names...")
print(f"URL: {SUPABASE_URL}")

# Test 1: Write to chat_history table with correct columns
print("\n=== TEST 1: Writing to chat_history ===")
chat_payload = {
    "user_id": "test123",
    "role": "user",
    "content": "Hello, this is a test message"  # Using 'content' instead of 'message'
}

try:
    res = requests.post(f"{SUPABASE_URL}/rest/v1/chat_history", headers=headers, json=chat_payload)
    print(f"WRITE STATUS: {res.status_code}")
    print(f"WRITE RESPONSE: {res.text}")
except Exception as e:
    print(f"WRITE ERROR: {e}")

# Test 2: Read from chat_history table
print("\n=== TEST 2: Reading from chat_history ===")
try:
    res2 = requests.get(f"{SUPABASE_URL}/rest/v1/chat_history", headers=headers, params={
        "user_id": "eq.test123",
        "order": "created_at.desc",  # Using 'created_at' instead of 'timestamp'
        "limit": "10"
    })
    print(f"READ STATUS: {res2.status_code}")
    print(f"READ RESPONSE: {res2.text}")
except Exception as e:
    print(f"READ ERROR: {e}")

print("\n=== TEST COMPLETE ===") 