"""
Complete end-to-end test of motivation generation
"""
import asyncio
import os
from services import MotivationService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_motivation_generation():
    """Test the complete motivation generation flow"""
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not set")
        return False
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║      Complete Motivation Generation Test                      ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()
    
    try:
        # Initialize service
        print("[1] Initializing MotivationService...")
        service = MotivationService(api_key=api_key)
        print("✅ Service initialized")
        print()
        
        # Test cases
        test_messages = [
            "Give me motivation to pass my exam",
            "I need encouragement to keep going",
            "Help me feel inspired",
        ]
        
        print("[2] Testing motivation generation...")
        print()
        
        for i, message in enumerate(test_messages, 1):
            print(f"   Test {i}/3: '{message}'")
            try:
                motivation = await service.generate_motivation(message)
                print(f"   ✅ Generated: {motivation}")
                print()
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                print()
                return False
        
        print("[3] Summary")
        print("✅ All tests passed!")
        print("✅ MotivationService is working correctly")
        print("✅ Your Telex agent should work now")
        print()
        print("Next steps:")
        print("  1. Push changes to GitHub: git push")
        print("  2. Wait for Vercel deployment (2-5 minutes)")
        print("  3. Send message to Telex agent")
        print("  4. Response should appear on dashboard")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_motivation_generation())
    exit(0 if success else 1)
