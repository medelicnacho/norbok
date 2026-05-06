import requests
from .chat import chat, check_ollama_env
from .ui import print_welcome, get_input, print_token, console

def run():
    check_ollama_env()
    session = requests.Session()
    messages = [
        {"role": "system", "content": "You are Norbok, a snarky but helpful coding tutor. Use >:3 as your only emoji. Never use real emojis."}
    ]
    print_welcome()
    while True:
        try:
            user_input = get_input()
        except (EOFError, KeyboardInterrupt):
            print("\nPeace brasskee >:3")
            break
        if user_input.strip().lower() == "exit":
            print("peace bro >:3")
            break
        messages.append({"role": "user", "content": user_input})
        console.print("[bold green]Norbok:[/bold green] ")
        reply = chat(session, messages, on_token=print_token)
        print()
        messages.append({"role": "assistant", "content": reply})
