import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 60)
print("Testing NEW FEATURES: ML, Employability, Adaptive Learning")
print("=" * 60)

# Use the user ID from previous test
user_id = "user_20260521205104"

# Test 1: Employability Score Endpoint
print("\n1. Testing /employability/<user_id> endpoint...")
try:
    response = requests.get(f"{BASE_URL}/employability/{user_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Adaptive Insights Endpoint
print("\n2. Testing /adaptive-insights/<user_id> endpoint...")
try:
    response = requests.get(f"{BASE_URL}/adaptive-insights/{user_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Chatbot with Employability Query
print("\n3. Testing /chat endpoint with employability query...")
try:
    response = requests.post(f"{BASE_URL}/chat", json={
        "message": "What's my employability score?",
        "userId": user_id
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Chatbot with Performance Query
print("\n4. Testing /chat endpoint with performance query...")
try:
    response = requests.post(f"{BASE_URL}/chat", json={
        "message": "How am I doing?",
        "userId": user_id
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("✅ New features testing completed!")
print("=" * 60)
