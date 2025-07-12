import os
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ✅ Save one chat message (user or agent)
async def save_chat_message(user_id: str, role: str, message: str) -> bool:
    url = f"{SUPABASE_URL}/rest/v1/chat_history"
    payload = {
        "user_id": user_id,
        "role": role,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=HEADERS, json=payload)
            res.raise_for_status()
            return True
    except Exception as e:
        print("[Supabase Save Error]", e)
        return False

# ✅ Fetch latest chat history for a user
async def get_chat_history(user_id: str, limit: int = 50) -> list:
    url = f"{SUPABASE_URL}/rest/v1/chat_history"
    params = {
        "user_id": f"eq.{user_id}",
        "order": "timestamp.desc",
        "limit": str(limit)
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=HEADERS, params=params)
            res.raise_for_status()
            data = res.json()
            return data[::-1]  # reverse to chronological order
    except Exception as e:
        print("[Supabase Fetch Error]", e)
        return []
