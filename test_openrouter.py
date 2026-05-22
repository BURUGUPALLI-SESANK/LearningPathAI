"""
Test script to verify OpenRouter API key and model
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free')
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'

print("=" * 80)
print("🧪 OpenRouter API Test")
print("=" * 80)

# Check API key
print(f"\n1️⃣ Checking API Key...")
if not OPENROUTER_API_KEY:
    print("❌ OPENROUTER_API_KEY not found in .env file!")
    print("Please add: OPENROUTER_API_KEY=sk-or-v1-...")
    exit(1)

print(f"✅ API Key found")
print(f"   Length: {len(OPENROUTER_API_KEY)} characters")
print(f"   Prefix: {OPENROUTER_API_KEY[:15]}...")
print(f"   Model: {OPENROUTER_MODEL}")

# Test API call
print(f"\n2️⃣ Testing API Connection...")

headers = {
    'Authorization': f'Bearer {OPENROUTER_API_KEY}',
    'Content-Type': 'application/json',
    'HTTP-Referer': 'http://localhost:5000',
    'X-Title': 'Learning Path Generator Test'
}

payload = {
    'model': OPENROUTER_MODEL,
    'messages': [
        {
            'role': 'user',
            'content': 'Say "Hello, API is working!" in JSON format: {"message": "your response"}'
        }
    ],
    'temperature': 0.7,
    'max_tokens': 100
}

try:
    print(f"📡 Sending request to: {OPENROUTER_URL}")
    print(f"📦 Model: {OPENROUTER_MODEL}")
    
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
    
    print(f"\n3️⃣ Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ HTTP 200 OK")
    else:
        print(f"❌ HTTP {response.status_code}")
        print(f"📄 Response: {response.text}")
        exit(1)
    
    # Parse response
    result = response.json()
    
    print(f"\n4️⃣ Response Structure:")
    print(f"📦 Keys: {list(result.keys())}")
    
    # Check structure
    if 'choices' in result:
        print(f"✅ 'choices' field present")
        print(f"   Choices count: {len(result['choices'])}")
        
        if result['choices'] and len(result['choices']) > 0:
            print(f"✅ choices[0] exists")
            
            choice = result['choices'][0]
            print(f"   Choice keys: {list(choice.keys())}")
            
            if 'message' in choice:
                print(f"✅ 'message' field present")
                message = choice['message']
                print(f"   Message keys: {list(message.keys())}")
                
                if 'content' in message:
                    print(f"✅ 'content' field present")
                    content = message['content']
                    print(f"\n5️⃣ AI Response:")
                    print(f"📝 {content}")
                    
                    print(f"\n{'=' * 80}")
                    print("✅ SUCCESS! OpenRouter API is working correctly!")
                    print("=" * 80)
                else:
                    print(f"❌ 'content' field missing in message")
                    print(f"📄 Message: {json.dumps(message, indent=2)}")
            else:
                print(f"❌ 'message' field missing in choice")
                print(f"📄 Choice: {json.dumps(choice, indent=2)}")
        else:
            print(f"❌ choices array is empty")
    else:
        print(f"❌ 'choices' field missing")
        print(f"📄 Full response: {json.dumps(result, indent=2)}")
    
    # Check for errors in response
    if 'error' in result:
        print(f"\n❌ API returned an error:")
        print(f"📄 {json.dumps(result['error'], indent=2)}")
        exit(1)
    
    # Show usage info if available
    if 'usage' in result:
        print(f"\n📊 Token Usage:")
        print(f"   Prompt tokens: {result['usage'].get('prompt_tokens', 'N/A')}")
        print(f"   Completion tokens: {result['usage'].get('completion_tokens', 'N/A')}")
        print(f"   Total tokens: {result['usage'].get('total_tokens', 'N/A')}")

except requests.exceptions.Timeout:
    print(f"❌ Request timed out after 30 seconds")
    print(f"   The API might be slow or unreachable")
    exit(1)

except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
    print(f"   Check your internet connection")
    exit(1)

except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error: {e}")
    print(f"📄 Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
    exit(1)

except json.JSONDecodeError as e:
    print(f"❌ Failed to parse JSON response: {e}")
    print(f"📄 Raw response: {response.text}")
    exit(1)

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    print(f"📄 Traceback:\n{traceback.format_exc()}")
    exit(1)
