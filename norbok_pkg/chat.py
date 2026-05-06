import requests
import json

def chat(messages, on_token):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwen2.5-coder:7b",
            "messages": messages,
            "stream": True
        },
        stream=True
    )
    full_reply = ""
    for line in response.iter_lines():
        if line:
            chunk = line.decode("utf-8")
            data = json.loads(chunk)
            token = data.get("message", {}).get("content", "")
            full_reply += token
            on_token(token)
    return full_reply
