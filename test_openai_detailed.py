"""
Enhanced OpenRouter API Test with detailed diagnostics
"""
import asyncio
import os
from openai import AsyncOpenAI
from httpx import Timeout
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_openrouter_detailed():
    """Test OpenRouter API with detailed diagnostics"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not set in environment")
        return
    
    print(f"✅ API Key found")
    print(f"   Key format: {api_key[:20]}...{api_key[-10:]}")
    print(f"   Key length: {len(api_key)}")
    print()
    
    # Check key format
    if not api_key.startswith("sk-or-v1-"):
        print("⚠️  WARNING: Key doesn't start with 'sk-or-v1-'")
        print("   OpenRouter keys should start with 'sk-or-v1-'")
        print()
    
    try:
        # Create client with timeout
        print("[1] Creating AsyncOpenAI client...")
        print(f"    Base URL: https://openrouter.ai/api/v1")
        print(f"    Timeout: 30 seconds")
        print()
        
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=Timeout(30.0)
        )
        print("✅ Client created successfully")
        print()
        
        # Make test request
        print("[2] Making test API call to OpenRouter...")
        print("    Model: gpt-3.5-turbo")
        print("    Request: 'Say hello'")
        print("    Max tokens: 50")
        print()
        print("    Sending... (this may take a few seconds)")
        print()
        
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "Say hello"}
                ],
                temperature=0.7,
                max_tokens=50,
            ),
            timeout=25.0
        )
        
        print("✅ API call succeeded!")
        print()
        print("📊 Response Details:")
        print(f"   Model: {response.model}")
        print(f"   Tokens used (prompt): {response.usage.prompt_tokens}")
        print(f"   Tokens used (completion): {response.usage.completion_tokens}")
        print(f"   Message: {response.choices[0].message.content}")
        print()
        print("✅ OpenRouter API is working correctly!")
        print()
        print("💡 Next steps:")
        print("   Your motivation agent should work on Telex now.")
        
    except Exception as e:
        print(f"❌ API call failed!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {e}")
        print()
        
        # Provide diagnostics
        print("🔍 Diagnostics:")
        
        if "401" in str(e):
            print("   🔴 Authentication Error (401)")
            print()
            print("   Possible causes:")
            print("      1. API key is invalid or expired")
            print("      2. API key doesn't have required permissions")
            print("      3. OpenRouter account issue")
            print()
            print("   Solutions:")
            print("      1. Generate new key at: https://openrouter.ai/keys")
            print("      2. Copy the full key (starts with sk-or-v1-)")
            print("      3. Update .env file with new key")
            print("      4. Restart the server")
            
        elif "429" in str(e):
            print("   🟡 Rate Limited (429)")
            print("   You've made too many requests.")
            print("   Wait a few minutes and try again.")
            
        elif "Timeout" in str(e) or "timeout" in str(e):
            print("   ⏱️  Timeout Error")
            print("   The API is taking too long to respond.")
            print("   Check your internet connection or try again.")
            
        elif "Connection" in str(e) or "connection" in str(e):
            print("   🌐 Connection Error")
            print("   Can't reach OpenRouter API.")
            print("   Check your internet connection.")
            
        else:
            print(f"   Unknown error: {type(e).__name__}")
            print("   Check the error message above for details.")
        
        print()
        print("📚 Resources:")
        print("   OpenRouter: https://openrouter.ai")
        print("   API Keys: https://openrouter.ai/keys")
        print("   Docs: https://openrouter.ai/docs")

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     Enhanced OpenRouter API Connectivity Test                  ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    asyncio.run(test_openrouter_detailed())
