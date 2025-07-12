#!/usr/bin/env python3
"""
Debug script to check why name recall isn't working
"""

import asyncio
import httpx
import json

async def debug_name_recall():
    """Debug name recall issue"""
    test_user_id = "debug_name_123"
    
    print("🔍 Debugging Name Recall...")
    print("=" * 50)
    
    # Step 1: Tell agent your name
    print("Step 1: Telling agent my name is Hamza")
    payload1 = {
        "user_id": test_user_id,
        "message": "my name is hamza"
    }
    async with httpx.AsyncClient() as client:
        res1 = await client.post(
            "http://127.0.0.1:8000/api/v1/agent/chat",
            json=payload1,
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        response1 = res1.json().get('response', '')
        print(f"✅ Response: {response1}")
    
    # Step 2: Check what's in Supabase
    print("\nStep 2: Checking Supabase data")
    async with httpx.AsyncClient() as client:
        res2 = await client.get(
            f"http://127.0.0.1:8000/api/v1/debug/supabase/{test_user_id}",
            timeout=10.0
        )
        data = res2.json()
        print(f"✅ Supabase data: {json.dumps(data, indent=2)}")
    
    # Step 3: Ask what is my name?
    print("\nStep 3: Asking 'what is my name?'")
    payload3 = {
        "user_id": test_user_id,
        "message": "what is my name?"
    }
    async with httpx.AsyncClient() as client:
        res3 = await client.post(
            "http://127.0.0.1:8000/api/v1/agent/chat",
            json=payload3,
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        response3 = res3.json().get('response', '')
        print(f"✅ Response: {response3}")

async def main():
    print("🚀 Starting Name Recall Debug...")
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/", timeout=5.0)
            print(f"✅ Server is running (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server not running: {e}")
        return
    
    await debug_name_recall()

if __name__ == "__main__":
    asyncio.run(main()) 