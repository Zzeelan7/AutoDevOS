#!/usr/bin/env python3
"""
Start AutoDevOS servers properly with correct working directory
"""
import os
import sys
import subprocess
import time

project_root = r"C:\Users\zzeel\OneDrive\Desktop\AutoDevOS"
os.chdir(project_root)

# Make sure we're in the right place
print(f"Working directory: {os.getcwd()}")
print()

# Start Backend (FastAPI on 8000)
print("[1] Starting FastAPI Backend on http://0.0.0.0:8000")
print("    (Press Ctrl+C in that window to stop)")
print()

backend_cmd = [
    sys.executable, "-m", "uvicorn", 
    "server.app:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload"
]

backend_proc = subprocess.Popen(
    backend_cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
    bufsize=1
)

# Wait for backend to start
time.sleep(3)

# Start Frontend (Next.js on 3000)
print()
print("[2] Starting Next.js Frontend on http://localhost:3000")
print("    (Press Ctrl+C in that window to stop)")
print()

os.chdir(os.path.join(project_root, "frontend"))
frontend_cmd = [
    "npm", "run", "dev"
]

frontend_proc = subprocess.Popen(
    frontend_cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    universal_newlines=True,
    bufsize=1
)

print()
print("="*50)
print("Both servers are starting...")
print(" Backend:  http://localhost:8000")
print(" Frontend: http://localhost:3000")
print("="*50)
print()

# Keep both processes running
try:
    backend_proc.wait()
except KeyboardInterrupt:
    backend_proc.terminate()
    frontend_proc.terminate()
    print("\nServers stopped.")
