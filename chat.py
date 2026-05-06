import os
from openai import OpenAI

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError("DEEPSEEK_API_KEY is not set. Run: source ~/.bashrc")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=30.0,
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
            model="deepseek-v4-flash",
            messages=messages,
            max_tokens=400,
            stream=True,
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