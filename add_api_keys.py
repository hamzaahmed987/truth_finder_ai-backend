#!/usr/bin/env python3
"""
Script to add API keys to .env file
"""

import os
from pathlib import Path

def add_api_keys():
    """Add the user's API keys to .env file"""
    
    # The user's API keys
    api_keys = {
        "GOOGLE_API_KEY": "AIzaSyBoS3XfM7WHyE8j2v1HZnUYxXZEVz65VC0",
        "TWITTER_API_KEY": "AIwzEeoFtLEBNGWjv2hmqbrJ1",
        "TWITTER_API_SECRET": "RgaFt26zJlqfD8DtTHAbPCVARyYYzFJwTgJDE983h31NfEL7og",
        "TWITTER_ACCESS_TOKEN": "1872349528998748160-6jVWfs7sa7Cbnrs9SQpskZKee2fS2j",
        "TWITTER_ACCESS_SECRET": "Leno8nduRTOrhP9Qau9gTNgs7XltqBE1ztTmhiX81kKAs"
    }
    
    env_file_path = Path(".env")
    
    if not env_file_path.exists():
        print("❌ .env file not found! Run 'python setup_env.py' first.")
        return
    
    try:
        # Read current .env file
        with open(env_file_path, 'r') as f:
            content = f.read()
        
        # Update with actual API keys
        updated_content = content
        for key, value in api_keys.items():
            # Replace placeholder values with actual keys
            placeholder = f"{key}=your_{key.lower()}_here"
            actual = f"{key}={value}"
            
            if placeholder in updated_content:
                updated_content = updated_content.replace(placeholder, actual)
            elif f"{key}=" in updated_content:
                # If key exists but with different placeholder, replace the whole line
                lines = updated_content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith(f"{key}="):
                        lines[i] = actual
                        break
                updated_content = '\n'.join(lines)
            else:
                # Add new key if it doesn't exist
                updated_content += f"\n{actual}"
        
        # Write updated content
        with open(env_file_path, 'w') as f:
            f.write(updated_content)
        
        print("✅ API keys added successfully!")
        print("\n📋 Added keys:")
        for key in api_keys.keys():
            print(f"   ✅ {key}")
        
        print("\n🎯 Next steps:")
        print("1. Run 'python test_agent.py' to test your setup")
        print("2. Start your backend with 'python run_server.py'")
        print("3. Start your frontend with 'npm run dev'")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")

if __name__ == "__main__":
    print("🔑 Adding API Keys to .env file...")
    add_api_keys() 