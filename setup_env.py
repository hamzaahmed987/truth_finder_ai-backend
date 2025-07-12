#!/usr/bin/env python3
"""
Setup script for Truth Finder AI Environment Variables
This script will help you create the .env file with the required API keys
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with required environment variables"""
    
    env_content = """# Truth Finder AI - Environment Variables
# Copy this file to .env and fill in your actual API keys

# Required: Google Gemini API Key (for AI analysis)
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Optional: Twitter API (for sentiment analysis)
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here

# Optional: Google Custom Search API (for fact checking)
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# Backend Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=True
"""
    
    env_file_path = Path(".env")
    
    if env_file_path.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully!")
        print("\n📝 Next steps:")
        print("1. Edit the .env file and add your actual API keys")
        print("2. At minimum, you need GOOGLE_API_KEY for basic functionality")
        print("3. Run 'python test_agent.py' to test your setup")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

def main():
    print("🤖 Truth Finder AI - Environment Setup")
    print("=" * 50)
    
    print("\nThis script will create a .env file with the required environment variables.")
    print("You'll need to edit it manually to add your actual API keys.")
    
    response = input("\nDo you want to create the .env file? (Y/n): ")
    if response.lower() in ['', 'y', 'yes']:
        create_env_file()
    else:
        print("Setup cancelled.")

if __name__ == "__main__":
    main() 