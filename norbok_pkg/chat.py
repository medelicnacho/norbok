import os
import openai

def check_api_key():
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise SystemExit("Error: DEEPSEEK_API_KEY environment variable not set.")

def chat(client, messages, model, on_token, check_stop=None):
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        temperature=0.7,
        max_tokens=2048,
    )
    full = []
    for chunk in stream:
        if check_stop and check_stop():
            break
        content = chunk.choices[0].delta.content
        if content:
            full.append(content)
            on_token(content)
    return "".join(full)
