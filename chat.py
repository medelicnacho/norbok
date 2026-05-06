from openai import OpenAI

client = OpenAI(
    api_key="ollama",  # Ollama doesn't require a real API key
    base_url="http://localhost:11434/v1",
    timeout=60.0,  # Reduced timeout for faster failure
)

messages = [
    {
        "role": "system",
        "content": "Python tutor. Be concise.",
    }
]

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
            max_tokens=200,  # Reduced for faster responses
            stream=True,
            temperature=0.3,  # Lower = faster generation
            top_p=0.9,  # Nucleus sampling for speed
            extra_body={
                "num_ctx": 1024,  # Minimum context for speed
                "keep_alive": "30m",  # Keep model loaded
                "num_predict": 200,  # Match max_tokens
                "repeat_penalty": 1.1,  # Faster by avoiding repetition
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
