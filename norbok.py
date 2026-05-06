import requests

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
    "model": "qwen2.5-coder:0.5b",
    "message": [
    {"role": "user", "content": "teach me a fundemental computer science concept in one short sentence"}
    ], 
    "stream": False
    }

)

data = response.json()
print(data["message"]["content"])