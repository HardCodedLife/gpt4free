 # test_ollama.py
import requests
import json

OLLAMA_URL = "http://100.92.194.37:11434"

# 1. Test network access + /api/tags endpoint
print("Testing /api/tags...")
response = requests.get(f"{OLLAMA_URL}/api/tags")
print(f"Status: {response.status_code}")
models = response.json()
print(f"Available models: {json.dumps(models, indent=2)}")

# 2. Test /api/chat endpoint (non-streaming)
print("\nTesting /api/chat (non-streaming)...")
chat_data = {
        "model": "deepseek-r1:14b",  # Replace with actual model name from step 1
        "messages": [{"role": "user", "content": "Hello!"}],
            "stream": False
            }
response = requests.post(f"{OLLAMA_URL}/api/chat", json=chat_data)
print(f"Response: {response.json()}")

# 3. Test streaming
print("\nTesting streaming...")
chat_data["stream"] = True
response = requests.post(f"{OLLAMA_URL}/api/chat", json=chat_data, stream=True)
for line in response.iter_lines():
    if line:
        print(json.loads(line))
