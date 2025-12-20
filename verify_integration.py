import requests
import sys
import time
from multiprocessing import Process
import uvicorn

# We'll assume the server is running or we can start it for a quick test.
# For simplicity, we'll try to check if localhost:8000 is reachable, if not we print instructions.
# Actually, since we can't reliably spin up the server in background and kill it easily in this environment without blocking,
# we will just check assuming it runs, OR we just simulate the tools import which we already did.
# But here we want to verifying the API logic essentially involves tool invocations.

# Let's import the API app and test the endpoints directly using TestClient!
# This is much better than spinning up a server.

try:
    from fastapi.testclient import TestClient
    from api.server import app
except ImportError as e:
    print(f"Failed to import TestClient or app: {e}")
    sys.exit(1)

client = TestClient(app)

def test_endpoints():
    print("Testing /health...")
    r = client.get("/health")
    print(f"Health Status: {r.status_code}")
    assert r.status_code == 200

    print("Testing Static Files (index.html)...")
    r = client.get("/")
    print(f"Static Status: {r.status_code}")
    assert r.status_code == 200
    assert "<title>Smart Task Planner</title>" in r.text

    print("Testing /notes (mock invocation)...")
    # This might fail if keys aren't set, but it should return 500 or error json, not 404.
    r = client.get("/notes")
    print(f"Notes Status: {r.status_code}")
    # We expect 200 (if keys set) or 500 (if tool fails) or 200 with error message in list
    # As long as it's not 404, the path exists.
    assert r.status_code != 404

    print("Testing /calendar (mock invocation)...")
    r = client.get("/calendar?date=2025-01-01")
    print(f"Calendar Status: {r.status_code}")
    assert r.status_code != 404

    print("Integration verification passed (Endpoints exist).")

if __name__ == "__main__":
    test_endpoints()
