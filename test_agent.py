#!/usr/bin/env python3
"""
Test script for Truth Finder AI Agent (Gemini Version)
Run this to test your AI agent functionality
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Now we can import our app modules
from app.agents import news_agent, multi_agent_system

# Load environment variables
load_dotenv()

async def test_agent():
    """Test the AI agent with sample news content"""
    
    print("🤖 Testing Truth Finder AI Agent (Gemini Version)...")
    print("=" * 60)
    
    # Sample news content for testing
    test_content = """
    Breaking: Scientists discover new planet in our solar system that could support life.
    The planet, named Kepler-442b, is located 1,200 light-years from Earth and has 
    similar conditions to our planet. NASA officials say this could be a major breakthrough 
    in the search for extraterrestrial life.
    """
    
    print(f"📰 Test Content: {test_content.strip()}")
    print("\n" + "=" * 60)
    
    try:
        # Test single agent analysis
        print("🔍 Running AI Agent Analysis...")
        result = await news_agent.analyze_news_advanced(test_content, "english")
        
        print("\n✅ Analysis Complete!")
        
        # Handle missing keys gracefully
        verdict = result.get('verdict', 'UNKNOWN')
        confidence = result.get('confidence', 0)
        agent_version = result.get('agent_version', 'Unknown')
        timestamp = result.get('timestamp', 'Unknown')
        analysis = result.get('analysis', 'No analysis available')
        error = result.get('error', None)
        
        if error:
            print(f"❌ Error: {error}")
        else:
            print(f"🎯 Verdict: {verdict}")
            print(f"📊 Confidence: {confidence}%")
            print(f"🤖 Agent Version: {agent_version}")
            print(f"⏰ Timestamp: {timestamp}")
            
            print("\n📋 Detailed Analysis:")
            print("-" * 40)
            print(analysis)
        
        # Test multi-agent system
        print("\n" + "=" * 60)
        print("🚀 Testing Multi-Agent System...")
        multi_result = await multi_agent_system.analyze_with_multiple_agents(test_content, "english")
        
        print("✅ Multi-Agent Analysis Complete!")
        print(f"📊 Number of agents: {len(multi_result)}")
        
        # Show multi-agent results
        for agent_name, agent_result in multi_result.items():
            print(f"\n🤖 {agent_name.upper()}:")
            if isinstance(agent_result, dict):
                agent_verdict = agent_result.get('verdict', 'UNKNOWN')
                agent_confidence = agent_result.get('confidence', 0)
                print(f"   Verdict: {agent_verdict}")
                print(f"   Confidence: {agent_confidence}%")
            else:
                print(f"   Result: {agent_result}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Make sure you have:")
        print("1. Set GOOGLE_API_KEY in your .env file")
        print("2. Installed all requirements: pip install -r requirements.txt")
        print("3. Your backend server is running")
        print("4. You have a valid Google API key with Gemini access")

if __name__ == "__main__":
    asyncio.run(test_agent()) 