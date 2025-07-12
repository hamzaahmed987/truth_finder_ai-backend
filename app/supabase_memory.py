import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


def save_memory(user_id: str, key: str, value: str) -> bool:
    """
    Save a key-value memory for a specific user to Supabase
    """
    url = f"{SUPABASE_URL}/rest/v1/memory"
    payload = {
        "user_id": user_id,
        "key": key,
        "value": value,
    }

    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"[Save Memory Error] {e}")
        return False


def get_memory(user_id: str, key: str) -> str | None:
    """
    Retrieve value for a specific user and key from Supabase
    """
    url = f"{SUPABASE_URL}/rest/v1/memory"
    params = {
        "user_id": f"eq.{user_id}",
        "key": f"eq.{key}",
        "select": "value",
        "limit": 1,
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        return data[0]["value"] if data else None
    except requests.exceptions.RequestException as e:
        print(f"[Get Memory Error] {e}")
        return None
