#!/usr/bin/env python3
"""
Direct server runner - Bypasses any caching issues
"""
import subprocess
import sys
import time
import os

os.chdir(r"c:\Users\zinsu\Desktop\motivation Agent")

# Kill any existing processes
subprocess.run(["taskkill", "/IM", "python.exe", "/F"], 
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)

# Start uvicorn
print("Starting server on port 8000...")
print("=" * 60)

result = subprocess.run([
    sys.executable, "-m", "uvicorn",
    "main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload"
], cwd=r"c:\Users\zinsu\Desktop\motivation Agent")

sys.exit(result.returncode)
