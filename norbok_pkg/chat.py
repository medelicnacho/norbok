import requests

def chat(messages):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwen2.5-coder:7b",
            "messages": messages,
            "stream": False
        }
    )
    return response.json()["message"]["content"]