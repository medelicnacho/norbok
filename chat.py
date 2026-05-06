import httpx
import requests
from openai import OpenAI

# Preload model into memory via Ollama API (no generation, just load weights)
try:
    requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "qwen2.5-coder:7b", "prompt": "", "keep_alive": "30m"},
        timeout=120,
    )
except Exception:
    pass

http_client = httpx.Client(
    limits=httpx.Limits(max_connections=1, max_keepalive_connections=1),
    timeout=60.0,
)

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    http_client=http_client,
)

MAX_HISTORY = 6  # Keep conversation short for speed

system_msg = {"role": "system", "content": "Python tutor. Be concise."}
messages = [system_msg]

print("Chat ready. Type 'exit' to quit.")

while True:
    user_msg = input("\nYou: ").strip()

    if user_msg.lower() in {"quit", "exit"}:
        break

    if not user_msg:
        continue

    messages.append({"role": "user", "content": user_msg})

    # Trim history to keep context small and fast
    if len(messages) > MAX_HISTORY + 1:  # +1 for system msg
        messages = [system_msg] + messages[-(MAX_HISTORY):]

    print("\nBot: ", end="", flush=True)

    try:
        stream = client.chat.completions.create(
            model="qwen2.5-coder:7b",
            messages=messages,
            max_tokens=200,
            stream=True,
            temperature=0.3,
            top_p=0.9,
            extra_body={
                "num_ctx": 1024,
                "keep_alive": "30m",
                "num_predict": 200,
                "repeat_penalty": 1.1,
                "num_batch": 512,  # Larger batch = faster prompt processing
            },
        )

        bot_msg = ""

        for chunk in stream:
            piece = chunk.choices[0].delta.content or ""
            print(piece, end="", flush=True)
            bot_msg += piece

        print()
        messages.append({"role": "assistant", "content": bot_msg})

    except KeyboardInterrupt:
        print("\nStopped.")
        break

    except Exception as e:
        print("\nERROR:")
        print(type(e).__name__)
        print(e)
