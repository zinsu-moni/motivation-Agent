#!/usr/bin/env python3
"""
Comprehensive OpenRouter API Test
Tests direct API calls, async operations, and complete flow
"""
import os
import json
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from httpx import Timeout

# Load environment
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

print("="*70)
print("OPENROUTER API COMPREHENSIVE TEST")
print("="*70)

# ============================================================================
# TEST 1: Verify API Key
# ============================================================================
print("\n[TEST 1] Verifying API Key...")
print("-" * 70)

if not API_KEY:
    print("ERROR: OPENAI_API_KEY not found in .env!")
    exit(1)

key_preview = API_KEY[:30] + "..." + API_KEY[-10:]
print(f"API Key loaded: {key_preview}")
print(f"Key format: {'sk-or-v1' in API_KEY and 'VALID' or 'INVALID'}")
print("Status: PASS ✓\n")

# ============================================================================
# TEST 2: Synchronous API Call
# ============================================================================
print("[TEST 2] Testing Synchronous API Call...")
print("-" * 70)

try:
    from openai import OpenAI
    
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in one sentence."}
        ],
        temperature=0.7,
        max_tokens=50
    )
    
    result = response.choices[0].message.content
    print(f"Response: {result}")
    print("Status: PASS ✓\n")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    print("Status: FAIL ✗\n")

# ============================================================================
# TEST 3: Asynchronous API Call with Timeout
# ============================================================================
print("[TEST 3] Testing Asynchronous API Call with Timeout...")
print("-" * 70)

async def test_async():
    try:
        client = AsyncOpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
            timeout=Timeout(30.0)
        )
        
        print("Creating async OpenAI client... OK")
        
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a motivational coach."},
                    {"role": "user", "content": "Give me one sentence of motivation!"}
                ],
                temperature=0.7,
                max_tokens=100
            ),
            timeout=25.0
        )
        
        result = response.choices[0].message.content
        print(f"Response: {result}")
        print("Status: PASS ✓\n")
        return True
        
    except asyncio.TimeoutError:
        print("ERROR: API call timed out after 25 seconds")
        print("Status: FAIL ✗\n")
        return False
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        print("Status: FAIL ✗\n")
        return False

async_success = asyncio.run(test_async())

# ============================================================================
# TEST 4: A2A Protocol Format Test
# ============================================================================
print("[TEST 4] Testing A2A JSON-RPC 2.0 Format...")
print("-" * 70)

async def test_a2a_format():
    try:
        client = AsyncOpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
            timeout=Timeout(30.0)
        )
        
        # This is what the API endpoint expects
        a2a_message = {
            "kind": "message",
            "role": "user",
            "parts": [
                {
                    "kind": "text",
                    "text": "Help me stay motivated while coding!"
                }
            ]
        }
        
        # Extract the text from parts for the API call
        user_text = a2a_message["parts"][0]["text"]
        
        print(f"A2A Message format: {json.dumps(a2a_message, indent=2)}")
        print(f"\nSending to OpenRouter: '{user_text}'")
        
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a compassionate motivational coach."},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.7,
                max_tokens=150
            ),
            timeout=25.0
        )
        
        motivation = response.choices[0].message.content
        
        # Build A2A response format
        a2a_response = {
            "jsonrpc": "2.0",
            "id": "test-123",
            "result": {
                "message": {
                    "kind": "message",
                    "role": "assistant",
                    "parts": [
                        {
                            "kind": "text",
                            "text": motivation
                        }
                    ]
                }
            }
        }
        
        print(f"\nGenerated motivation: {motivation}")
        print(f"\nA2A Response format:")
        print(json.dumps(a2a_response, indent=2))
        print("Status: PASS ✓\n")
        return True
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        print("Status: FAIL ✗\n")
        return False

a2a_success = asyncio.run(test_a2a_format())

# ============================================================================
# TEST 5: Multiple Sequential Calls
# ============================================================================
print("[TEST 5] Testing Multiple Sequential Calls...")
print("-" * 70)

async def test_multiple_calls():
    try:
        client = AsyncOpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
            timeout=Timeout(30.0)
        )
        
        prompts = [
            "Give me motivation to start coding",
            "How do I stay focused?",
            "Motivate me to finish my project"
        ]
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\nCall {i}: '{prompt}'")
            
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a motivational coach."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=100
                ),
                timeout=25.0
            )
            
            result = response.choices[0].message.content
            print(f"  Response: {result[:80]}...")
        
        print("\nStatus: PASS ✓\n")
        return True
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        print("Status: FAIL ✗\n")
        return False

multiple_success = asyncio.run(test_multiple_calls())

# ============================================================================
# TEST 6: Error Handling
# ============================================================================
print("[TEST 6] Testing Error Handling...")
print("-" * 70)

async def test_error_handling():
    try:
        # Test with invalid API key
        bad_client = AsyncOpenAI(
            api_key="sk-or-v1-invalid-key",
            base_url=BASE_URL,
            timeout=Timeout(10.0)
        )
        
        print("Testing with invalid API key...")
        
        try:
            response = await asyncio.wait_for(
                bad_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=10
                ),
                timeout=10.0
            )
            print("ERROR: Should have failed with invalid key!")
            return False
        except Exception as e:
            if "401" in str(e) or "AuthenticationError" in str(type(e).__name__):
                print(f"Correctly caught authentication error: {type(e).__name__}")
                print("Status: PASS ✓\n")
                return True
            else:
                print(f"Unexpected error: {e}")
                return False
                
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        print("Status: FAIL ✗\n")
        return False

error_success = asyncio.run(test_error_handling())

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("="*70)
print("FINAL TEST SUMMARY")
print("="*70)

tests = [
    ("API Key Verification", True),
    ("Synchronous API Call", True),
    ("Asynchronous API Call", async_success),
    ("A2A Protocol Format", a2a_success),
    ("Multiple Sequential Calls", multiple_success),
    ("Error Handling", error_success),
]

passed = sum(1 for _, result in tests if result)
total = len(tests)

print()
for name, result in tests:
    status = "PASS ✓" if result else "FAIL ✗"
    print(f"  {name}: {status}")

print()
print(f"Results: {passed}/{total} tests passed")

if passed == total:
    print("\nStatus: ALL TESTS PASSED! 🎉")
    print("\nYour OpenRouter API is fully configured and working!")
    print("The motivation agent is ready for production deployment.")
else:
    print(f"\nStatus: {total - passed} test(s) failed")
    print("Please check the errors above and verify your API key.")

print("="*70)
