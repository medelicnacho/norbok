from openai import OpenAI

client = OpenAI(
    api_key="ollama",  # Ollama doesn't require a real API key
    base_url="http://localhost:11434/v1",
    timeout=120.0,  # Increased timeout for initial model loading
)

messages = [
    {
        "role": "system",
        "content": (
            "You are a strict but helpful Python tutor. "
            "Explain clearly. Keep answers short unless asked for detail."
        ),
    }
]

# Warmup: preload the model into memory
print("Loading model...", flush=True)
try:
    warmup = client.chat.completions.create(
        model="qwen2.5-coder:14b",
        messages=[{"role": "user", "content": "Hi"}],
        max_tokens=5,
        stream=False,
    )
    print("Model loaded. Chat ready. Type 'exit' to quit.")
except Exception as e:
    print(f"Warning: Could not preload model: {e}")
    print("Chat ready. Type 'exit' to quit.")

while True:
    user_msg = input("\nYou: ").strip()

    if user_msg.lower() in {"quit", "exit"}:
        break

    if not user_msg:
        continue

    messages.append({"role": "user", "content": user_msg})

    print("\nBot: ", end="", flush=True)

    try:
        stream = client.chat.completions.create(
            model="qwen2.5-coder:14b",
            messages=messages,
            max_tokens=400,
            stream=True,
            extra_body={
                "num_ctx": 4096,  # Context window size
                "keep_alive": "5m",  # Keep model in memory for 5 minutes
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
