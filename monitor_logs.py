"""
Real-time log monitor for the motivation agent
Tracks the complete flow from request to webhook delivery
"""
import subprocess
import sys
from datetime import datetime
import time

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print the header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║     Real-Time Motivation Agent Log Monitor                     ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

def track_phase(text, status="progress"):
    """Print a tracking phase with emoji and color"""
    if status == "progress":
        emoji = "⏳"
        color = Colors.YELLOW
    elif status == "success":
        emoji = "✅"
        color = Colors.GREEN
    elif status == "error":
        emoji = "❌"
        color = Colors.RED
    elif status == "info":
        emoji = "ℹ️"
        color = Colors.CYAN
    else:
        emoji = "•"
        color = Colors.BLUE
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}{emoji} [{timestamp}] {text}{Colors.ENDC}")

def monitor_logs():
    """Monitor server logs in real-time"""
    print_header()
    
    track_phase("Starting log monitor...", "info")
    track_phase("Waiting for requests from Telex...", "progress")
    track_phase("Make sure your server is running: python main.py", "info")
    
    print(f"\n{Colors.BOLD}Expected Flow:{Colors.ENDC}\n")
    print(f"  {Colors.CYAN}1. [REQUEST] Received A2A request{Colors.ENDC}")
    print(f"  {Colors.CYAN}2. [WEBHOOK] Starting background task{Colors.ENDC}")
    print(f"  {Colors.CYAN}3. [SERVICE] Making API call{Colors.ENDC}")
    print(f"  {Colors.CYAN}4. [SERVICE] API call completed successfully{Colors.ENDC}")
    print(f"  {Colors.CYAN}5. [WEBHOOK] Generated motivation{Colors.ENDC}")
    print(f"  {Colors.CYAN}6. [WEBHOOK] Response status: 200{Colors.ENDC}")
    print(f"  {Colors.CYAN}7. [WEBHOOK] SUCCESS - Response delivered to Telex!{Colors.ENDC}")
    print()
    
    track_phase("Send a message to your Telex agent now...", "info")
    track_phase("Monitoring for logs...", "progress")
    print()

def analyze_log_line(line):
    """Analyze a log line and return tracking info"""
    
    key_phrases = {
        "[REQUEST] Received A2A request": ("REQUEST received from Telex", "success"),
        "[REQUEST] Webhook URL:": ("Webhook config found", "success"),
        "[WEBHOOK] Starting background": ("Background task started", "success"),
        "[SERVICE] Making API call": ("Calling OpenRouter API", "progress"),
        "[SERVICE] API call completed successfully": ("OpenRouter responded", "success"),
        "[SERVICE] Raw response:": ("Got motivation from API", "success"),
        "[WEBHOOK] Generated motivation:": ("Motivation ready to send", "success"),
        "[WEBHOOK] Sending POST to:": ("Posting to webhook", "progress"),
        "[WEBHOOK] Response status: 200": ("Telex accepted webhook", "success"),
        "[WEBHOOK] SUCCESS": ("Response delivered to Telex!", "success"),
        
        # Errors
        "[SERVICE] API call timed out": ("API timeout - using fallback", "error"),
        "[SERVICE] ERROR": ("Service error occurred", "error"),
        "[WEBHOOK] ERROR": ("Webhook delivery failed", "error"),
        "[WEBHOOK] FAILED": ("Webhook POST failed", "error"),
        "ERROR": ("Error detected", "error"),
    }
    
    for phrase, (message, status) in key_phrases.items():
        if phrase in line:
            return message, status
    
    return None, None

if __name__ == "__main__":
    monitor_logs()
    
    print(f"{Colors.BOLD}Key Events to Watch For:{Colors.ENDC}\n")
    
    events = [
        ("[REQUEST] Received A2A request", "✅ Request received"),
        ("[SERVICE] Making API call", "⏳ API call in progress"),
        ("[SERVICE] API call completed successfully", "✅ API responded"),
        ("[WEBHOOK] SUCCESS", "✅ Response delivered to Telex"),
    ]
    
    for log_phrase, description in events:
        print(f"  • {log_phrase}")
        print(f"    → {description}\n")
    
    print(f"{Colors.GREEN}{Colors.BOLD}")
    print("Ready to monitor! Send a test message to your Telex agent.")
    print("Check the terminal running 'python main.py' for logs.")
    print(f"{Colors.ENDC}\n")
