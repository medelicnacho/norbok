import requests

# Fixed the request payload key from "message" to "messages" because the
# Ollama /api/chat endpoint expects the key "messages" (plural).
response = requests.post(
    "http://localhost:11434/api/chat",
    json={
    "model": "qwen2.5-coder:0.5b",
    "messages": [
    {"role": "user", "content": "teach me a fundemental computer science concept in one short sentence"}
    ], 
    "stream": False
    }

)

data = response.json()
print(data["message"]["content"])
