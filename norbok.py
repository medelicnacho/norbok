# Fixed: double colon '::' changed to single colon ':'
import requests

response = requests.post("http://localhost:11434/api/chat", json={
    "model": "qwen2.5-coder:7b",
    "messages": [{"role": "user", "content": "hello"}],
    "stream": False
    })

data = response.json()
print(data["message"]["content"])
