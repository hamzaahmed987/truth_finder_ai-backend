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

print(f"Testing Supabase connection...")
print(f"URL: {SUPABASE_URL}")
print(f"Key set: {bool(SUPABASE_KEY)}")

# Test 1: Write to chat_history table
print("\n=== TEST 1: Writing to chat_history ===")
chat_payload = {
    "user_id": "test123",
    "role": "user",
    "message": "Hello, this is a test message",
    "timestamp": datetime.utcnow().isoformat()
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
        "order": "timestamp.desc",
        "limit": "10"
    })
    print(f"READ STATUS: {res2.status_code}")
    print(f"READ RESPONSE: {res2.text}")
except Exception as e:
    print(f"READ ERROR: {e}")

# Test 3: Test the API endpoint directly
print("\n=== TEST 3: Testing API endpoint ===")
try:
    api_payload = {
        "user_id": "test123",
        "message": "Test message from API",
        "session_id": "test_session"
    }
    res3 = requests.post("http://127.0.0.1:8000/api/v1/agent/chat", json=api_payload)
    print(f"API STATUS: {res3.status_code}")
    print(f"API RESPONSE: {res3.text}")
except Exception as e:
    print(f"API ERROR: {e}")

print("\n=== TEST COMPLETE ===") 