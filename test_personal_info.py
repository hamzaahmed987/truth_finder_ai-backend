#!/usr/bin/env python3
"""
Test script to check if the improved agent remembers personal information
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_personal_info_memory():
    """Test if the agent remembers personal information correctly"""
    test_user_id = "hamza_test_789"
    session_id = "session_789"
    
    print("🧪 Testing Personal Information Memory...")
    print("=" * 60)
    
    # Step 1: Tell the agent your name
    print("Step 1: Telling agent my name is Hamza")
    payload1 = {
        "user_id": test_user_id,
        "message": "my name is hamza",
        "session_id": session_id
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
    
    # Step 2: Tell the agent you're from Karachi
    print("\nStep 2: Telling agent I'm from Karachi")
    payload2 = {
        "user_id": test_user_id,
        "message": "i'm from karachi",
        "session_id": session_id
    }
    async with httpx.AsyncClient() as client:
        res2 = await client.post(
            "http://127.0.0.1:8000/api/v1/agent/chat",
            json=payload2,
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        response2 = res2.json().get('response', '')
        print(f"✅ Response: {response2}")
    
    # Step 3: Tell the agent you're a web developer
    print("\nStep 3: Telling agent I'm a web developer")
    payload3 = {
        "user_id": test_user_id,
        "message": "i'm a web developer",
        "session_id": session_id
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
    
    print("\n" + "=" * 60)
    print("🔍 NOW TESTING RECALL...")
    print("=" * 60)
    
    # Step 4: Ask what is my name?
    print("\nStep 4: Asking 'what is my name?'")
    payload4 = {
        "user_id": test_user_id,
        "message": "what is my name?",
        "session_id": session_id
    }
    async with httpx.AsyncClient() as client:
        res4 = await client.post(
            "http://127.0.0.1:8000/api/v1/agent/chat",
            json=payload4,
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        response4 = res4.json().get('response', '')
        print(f"✅ Response: {response4}")
    
    # Step 5: Ask where am I from?
    print("\nStep 5: Asking 'where am i from?'")
    payload5 = {
        "user_id": test_user_id,
        "message": "where am i from?",
        "session_id": session_id
    }
    async with httpx.AsyncClient() as client:
        res5 = await client.post(
            "http://127.0.0.1:8000/api/v1/agent/chat",
            json=payload5,
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        response5 = res5.json().get('response', '')
        print(f"✅ Response: {response5}")
    
    # Step 6: Ask what is my job?
    print("\nStep 6: Asking 'what is my job?'")
    payload6 = {
        "user_id": test_user_id,
        "message": "what is my job?",
        "session_id": session_id
    }
    async with httpx.AsyncClient() as client:
        res6 = await client.post(
            "http://127.0.0.1:8000/api/v1/agent/chat",
            json=payload6,
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        response6 = res6.json().get('response', '')
        print(f"✅ Response: {response6}")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print("=" * 60)
    print(f"Name recall: {'✅' if 'hamza' in response4.lower() else '❌'}")
    print(f"Location recall: {'✅' if 'karachi' in response5.lower() else '❌'}")
    print(f"Job recall: {'✅' if 'web developer' in response6.lower() else '❌'}")
    print("\n🏁 Test completed!")

async def main():
    print("🚀 Starting Personal Information Memory Test...")
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/", timeout=5.0)
            print(f"✅ Server is running (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server not running: {e}")
        print("Please start the server with: uvicorn app.main:app --reload")
        return
    
    await test_personal_info_memory()

if __name__ == "__main__":
    asyncio.run(main()) 