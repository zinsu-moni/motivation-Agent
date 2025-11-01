"""
Diagnostic script to test the webhook flow locally
"""
import asyncio
import json
import httpx
from datetime import datetime

# Sample Telex A2A request format
SAMPLE_REQUEST = {
    "jsonrpc": "2.0",
    "id": "test-request-123",
    "method": "message/send",
    "params": {
        "message": {
            "kind": "message",
            "role": "user",
            "parts": [
                {"kind": "text", "text": "Give me motivation to study"}
            ],
            "messageId": "msg-123"
        },
        "configuration": {
            "acceptedOutputModes": ["text/plain"],
            "historyLength": 0,
            "pushNotificationConfig": {
                "url": "https://ping.telex.im/v1/a2a/webhooks/test-webhook",
                "token": "test-jwt-token-here",
                "authentication": {"schemes": ["Bearer"]}
            },
            "blocking": False
        }
    }
}

async def test_endpoint():
    """Test the endpoint with sample data"""
    print("=" * 60)
    print("WEBHOOK DIAGNOSTIC TEST")
    print("=" * 60)
    print(f"\n📝 Time: {datetime.now().isoformat()}")
    print(f"\n📤 Sample Request:")
    print(json.dumps(SAMPLE_REQUEST, indent=2))
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"\n🚀 Sending POST to http://localhost:8000/a2a/motivation")
            resp = await client.post(
                "http://localhost:8000/a2a/motivation",
                json=SAMPLE_REQUEST,
                timeout=30.0
            )
            
            print(f"\n📥 Response Status: {resp.status_code}")
            print(f"📥 Response Headers: {dict(resp.headers)}")
            print(f"📥 Response Body:")
            print(json.dumps(resp.json(), indent=2))
            
            print("\n⏳ Waiting 3 seconds for background task to complete...")
            await asyncio.sleep(3)
            
            print("\n✅ Test complete. Check server logs for [WEBHOOK] entries")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n💡 Make sure to run: python main.py")
    print("💡 Then in another terminal, run: python test_webhook.py\n")
    asyncio.run(test_endpoint())
