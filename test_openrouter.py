"""
Diagnostic script to test OpenRouter API connectivity
"""
import asyncio
import os
from openai import AsyncOpenAI
from httpx import Timeout
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_openrouter():
    """Test OpenRouter API connectivity and response time"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not set in environment")
        return
    
    print(f"✅ API Key found: {api_key[:20]}...")
    print()
    
    try:
        # Create client with timeout
        print("[1] Creating AsyncOpenAI client with 30s timeout...")
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=Timeout(30.0)
        )
        print("✅ Client created")
        print()
        
        # Make test request
        print("[2] Making test API call to OpenRouter...")
        print("    - Model: gpt-3.5-turbo")
        print("    - Message: 'Hello'")
        print("    - Timeout: 25s")
        print()
        
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are helpful."},
                    {"role": "user", "content": "Hello, just say 'hi'"}
                ],
                temperature=0.7,
                max_tokens=50,
            ),
            timeout=25.0
        )
        
        print("✅ API call succeeded!")
        print(f"   Response: {response.choices[0].message.content[:50]}...")
        print()
        print("✅ OpenRouter is working correctly")
        
    except asyncio.TimeoutError:
        print("❌ API call timed out after 25 seconds")
        print("   This means either:")
        print("   - OpenRouter is slow")
        print("   - Network connection is slow")
        print("   - Vercel cold start is slow")
        
    except Exception as e:
        print(f"❌ API call failed: {type(e).__name__}: {e}")
        print()
        print("Possible issues:")
        print("   - Invalid API key")
        print("   - Network connectivity")
        print("   - OpenRouter service down")
        print("   - Rate limited")

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║         OpenRouter API Connectivity Test                       ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    asyncio.run(test_openrouter())
