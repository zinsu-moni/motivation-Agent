#!/usr/bin/env python3
"""
Interactive API Key Update Tool
Helps you update the .env file with a new OpenRouter API key
"""
import os
from pathlib import Path

def main():
    print("="*70)
    print("OPENROUTER API KEY UPDATE TOOL")
    print("="*70)
    print()
    
    env_path = Path(r"c:\Users\zinsu\Desktop\motivation Agent\.env")
    
    print("STEP 1: Get your new API key")
    print("-" * 70)
    print("1. Go to: https://openrouter.ai/account/api-keys")
    print("2. Click 'Create New Key' or 'Generate Key'")
    print("3. Copy the full key (starts with sk-or-v1-)")
    print()
    
    new_key = input("Paste your new API key here: ").strip()
    
    # Validate key format
    if not new_key.startswith("sk-or-v1-"):
        print("ERROR: Key doesn't start with 'sk-or-v1-'")
        print("Make sure you copied the entire key!")
        return False
    
    if len(new_key) < 50:
        print("ERROR: Key seems too short")
        print("Make sure you copied the ENTIRE key")
        return False
    
    print()
    print("STEP 2: Updating .env file")
    print("-" * 70)
    
    # Read current .env
    if not env_path.exists():
        print(f"ERROR: .env file not found at {env_path}")
        return False
    
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Update the API key line
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("OPENAI_API_KEY="):
            old_key = line.strip().split("=", 1)[1][:20] + "..."
            lines[i] = f"OPENAI_API_KEY={new_key}\n"
            updated = True
            print(f"Updated API key from: {old_key}")
            print(f"Updated API key to:   {new_key[:20]}...")
            break
    
    if not updated:
        print("ERROR: Could not find OPENAI_API_KEY line in .env")
        return False
    
    # Write updated .env
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print()
    print("STEP 3: Verify update")
    print("-" * 70)
    
    # Read back to confirm
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith("OPENAI_API_KEY="):
                stored_key = line.strip().split("=", 1)[1]
                if stored_key == new_key:
                    print("✓ .env file successfully updated!")
                    print(f"  Key stored: {stored_key[:30]}...")
                    return True
                else:
                    print("ERROR: Key mismatch after update")
                    return False
    
    return False

if __name__ == "__main__":
    print()
    success = main()
    print()
    print("="*70)
    if success:
        print("SUCCESS! Your API key has been updated.")
        print()
        print("NEXT STEP: Run the test to verify it works")
        print("  python test_openrouter_complete.py")
        print()
        print("You should see: 'ALL TESTS PASSED! 🎉'")
    else:
        print("FAILED! Please check the error above.")
    print("="*70)
    print()
