"""
Log capture and analysis tool - Captures complete request/response cycle
"""
import sys
from datetime import datetime
from enum import Enum

class Phase(Enum):
    REQUEST = "REQUEST"
    WEBHOOK = "WEBHOOK"
    SERVICE = "SERVICE"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"

class LogAnalyzer:
    def __init__(self):
        self.phases = []
        self.start_time = None
        self.end_time = None
    
    def analyze_line(self, line):
        """Analyze a log line and extract phase information"""
        
        # Extract timestamp
        try:
            # Format: "2025-11-01 17:08:57"
            timestamp = line.split(" ")[0] + " " + line.split(" ")[1]
        except:
            timestamp = "N/A"
        
        # Determine phase
        phase_type = None
        message = None
        status = None
        
        if "[REQUEST]" in line:
            phase_type = Phase.REQUEST
            if "Received A2A request" in line:
                message = "A2A request received"
                status = "✅"
            elif "Webhook URL:" in line:
                message = "Webhook URL detected"
                status = "✅"
            elif "Webhook token present" in line:
                message = "Authentication token found"
                status = "✅"
        
        elif "[WEBHOOK]" in line:
            phase_type = Phase.WEBHOOK
            if "Starting background task" in line:
                message = "Background task started"
                status = "✅"
            elif "Generated motivation" in line:
                message = "Motivation generated"
                status = "✅"
            elif "Sending POST to" in line:
                message = "Posting to webhook"
                status = "⏳"
            elif "Response status: 200" in line:
                message = "Telex accepted response"
                status = "✅"
            elif "SUCCESS" in line:
                message = "Response delivered successfully"
                status = "✅"
            elif "FAILED" in line or "ERROR" in line:
                message = "Webhook delivery failed"
                status = "❌"
        
        elif "[SERVICE]" in line:
            phase_type = Phase.SERVICE
            if "Calling OpenRouter" in line:
                message = "OpenRouter API call initiated"
                status = "⏳"
            elif "Making API call" in line:
                message = "API call in progress"
                status = "⏳"
            elif "API call completed successfully" in line:
                message = "OpenRouter responded"
                status = "✅"
            elif "Raw response:" in line:
                message = "Response received from API"
                status = "✅"
            elif "API call timed out" in line:
                message = "API timeout - using fallback"
                status = "⚠️"
            elif "ERROR" in line:
                message = "Service error"
                status = "❌"
        
        return {
            "timestamp": timestamp,
            "phase": phase_type,
            "message": message,
            "status": status,
            "raw": line
        }

def display_flow():
    """Display the expected flow"""
    print("\n" + "="*70)
    print("EXPECTED COMPLETE LOG FLOW")
    print("="*70 + "\n")
    
    flow = [
        ("REQUEST", "✅", "Received A2A request"),
        ("REQUEST", "✅", "Webhook config present"),
        ("REQUEST", "✅", "Webhook token present"),
        ("WEBHOOK", "✅", "Starting background task"),
        ("SERVICE", "⏳", "Calling OpenRouter for motivation"),
        ("SERVICE", "⏳", "Making API call..."),
        ("SERVICE", "✅", "API call completed successfully"),
        ("SERVICE", "✅", "Raw response: [motivation text]"),
        ("WEBHOOK", "✅", "Generated motivation: [text]"),
        ("WEBHOOK", "⏳", "Sending POST to webhook"),
        ("WEBHOOK", "✅", "Response status: 200"),
        ("WEBHOOK", "✅", "SUCCESS - Response delivered to Telex!"),
    ]
    
    for phase, status, message in flow:
        phase_color = {
            "REQUEST": "\033[94m",  # Blue
            "WEBHOOK": "\033[96m",  # Cyan
            "SERVICE": "\033[92m",  # Green
        }.get(phase, "\033[0m")
        
        print(f"{phase_color}[{phase:8s}]{'\033[0m'} {status} {message}")
    
    print("\n" + "="*70)

def main():
    print("\n" + "="*70)
    print("LOG CAPTURE & ANALYSIS TOOL")
    print("="*70)
    
    print("\n📝 CAPTURING LOGS...")
    print("Make sure your server is running: python main.py")
    print("Send a message to your Telex agent to generate logs.\n")
    
    display_flow()
    
    print("\n📊 WHAT TO LOOK FOR:\n")
    
    indicators = [
        ("✅ [SERVICE] API call completed successfully", "API responded - good sign!"),
        ("✅ [WEBHOOK] SUCCESS", "End-to-end success - response delivered!"),
        ("❌ [SERVICE] API call timed out", "API slow - fallback used instead"),
        ("❌ [WEBHOOK] Response status: 401", "Auth token issue"),
        ("❌ [WEBHOOK] FAILED", "Webhook delivery failed"),
    ]
    
    for indicator, meaning in indicators:
        print(f"  {indicator}")
        print(f"    → {meaning}\n")
    
    print("="*70)
    print("\n💡 INSTRUCTIONS:\n")
    print("1. Copy the complete log sequence from your server")
    print("2. Look for all phases from REQUEST through WEBHOOK SUCCESS")
    print("3. Share the complete output showing the final status\n")

if __name__ == "__main__":
    main()
