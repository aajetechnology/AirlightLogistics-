# run_both.py  ← FINAL WORKING VERSION
import subprocess
import time
import sys

print("Starting Student Safe Travel — Django + FastAPI 🔥")

# Start Django
django = subprocess.Popen([sys.executable, "manage.py", "runserver", "8000"])

# Give Django 4 seconds to start
print("Waiting for Django to wake up on port 8000...")
time.sleep(4)

# Start FastAPI
fastapi = subprocess.Popen(["uvicorn", "api.main:app", "--port", "8001", "--reload"])

print("")
print("DJANGO → http://127.0.0.1:8000")
print("FASTAPI → http://127.0.0.1:8001")
print("ADMIN → http://127.0.0.1:8000/admin/")
print("")
print("Both running! Press Ctrl+C to stop")

try:
    django.wait()
    fastapi.wait()
except KeyboardInterrupt:
    print("\nShutting down safely...")
    django.terminate()
    fastapi.terminate()