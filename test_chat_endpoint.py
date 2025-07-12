#!/usr/bin/env python3
"""
Test script to check the chat endpoint functionality
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_chat_endpoint():
    """Test the chat endpoint"""
    
    print("🧪 Testing Chat Endpoint...")
    
    # Test data
    test_user_id = "test_user_123"
    test_message = "Hello, my name is Hamza"
    
    payload = {
        "user_id": test_user_id,
        "message": test_message,
        "session_id": "test_session_123"
    }
    
    print(f"📤 Sending payload: {json.dumps(payload, indent=2)}")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test the chat endpoint
            response = await client.post(
                "http://127.0.0.1:8000/api/v1/agent/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Response: {json.dumps(data, indent=2)}")
                
                # Check if history is returned
                if 'history' in data:
                    print(f"📚 History count: {len(data['history'])}")
                    for i, msg in enumerate(data['history']):
                        print(f"  {i+1}. {msg['role']}: {msg['content'][:50]}...")
                else:
                    print("⚠️  No history returned")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"❌ Response text: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

async def test_supabase_debug():
    """Test the Supabase debug endpoint"""
    
    print("\n🔍 Testing Supabase Debug Endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://127.0.0.1:8000/api/v1/debug/supabase/test_user_123",
                timeout=10.0
            )
            
            print(f"📥 Debug response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Debug info: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Debug error: {response.text}")
                
    except Exception as e:
        print(f"❌ Debug exception: {e}")

async def test_chat_remember_name():
    """Test if the agent remembers the user's name"""
    test_user_id = "test_user_123"
    session_id = "test_session_123"
    
    # Step 1: Tell the agent your name
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
        print(f"Step 1: Sent 'my name is hamza' | Status: {res1.status_code}")
        print(f"Response: {res1.json().get('response')}")
    
    # Step 2: Ask the agent what your name is
    payload2 = {
        "user_id": test_user_id,
        "message": "what is my name?",
        "session_id": session_id
    }
    async with httpx.AsyncClient() as client:
        res2 = await client.post(
            "http://127.0.0.1:8000/api/v1/agent/chat",
            json=payload2,
            headers={"Content-Type": "application/json"},
            timeout=30.0
        )
        print(f"Step 2: Sent 'what is my name?' | Status: {res2.status_code}")
        print(f"Response: {res2.json().get('response')}")

async def test_chat_remember_personal_info():
    """Test if the agent remembers multiple pieces of personal information"""
    test_user_id = "test_user_456"
    session_id = "test_session_456"
    
    print("\n🧪 Testing Personal Information Memory...")
    
    # Step 1: Tell the agent your name
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
        print(f"Step 1: Sent 'my name is hamza' | Status: {res1.status_code}")
        print(f"Response: {res1.json().get('response')}")
    
    # Step 2: Tell the agent you're from Karachi
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
        print(f"Step 2: Sent 'i'm from karachi' | Status: {res2.status_code}")
        print(f"Response: {res2.json().get('response')}")
    
    # Step 3: Tell the agent you're a web developer
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
        print(f"Step 3: Sent 'i'm a web developer' | Status: {res3.status_code}")
        print(f"Response: {res3.json().get('response')}")
    
    # Step 4: Ask what is my name?
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
        print(f"Step 4: Sent 'what is my name?' | Status: {res4.status_code}")
        print(f"Response: {res4.json().get('response')}")
    
    # Step 5: Ask where am I from?
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
        print(f"Step 5: Sent 'where am i from?' | Status: {res5.status_code}")
        print(f"Response: {res5.json().get('response')}")
    
    # Step 6: Ask what is my job?
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
        print(f"Step 6: Sent 'what is my job?' | Status: {res6.status_code}")
        print(f"Response: {res6.json().get('response')}")

async def main():
    print("🚀 Starting Chat Endpoint Tests...")
    print("=" * 50)
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/", timeout=5.0)
            print(f"✅ Server is running (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Server not running: {e}")
        print("Please start the server with: uvicorn app.main:app --reload")
        return
    
    # Test Supabase debug first
    await test_supabase_debug()
    
    # Test chat endpoint
    await test_chat_endpoint()
    
    # Test if agent remembers the name
    await test_chat_remember_name()
    
    # Test if agent remembers multiple pieces of personal info
    await test_chat_remember_personal_info()
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")

if __name__ == "__main__":
    asyncio.run(main()) 