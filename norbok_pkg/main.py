import requests
import signal
from .chat import chat, check_ollama_env
from .ui import print_welcome, get_input, print_token, print_reply, console

def run():
    check_ollama_env()
    session = requests.Session()
    # adapter with keep-alive and no retries (fail fast on a streaming endpoint)
    session.mount("http://", requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1))

    stop_generation = False
    def handle_sigint(sig, frame):
        nonlocal stop_generation
        stop_generation = True

    original_sigint = signal.signal(signal.SIGINT, handle_sigint)

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
        reply = chat(session, messages, on_token=print_token, check_stop=lambda: stop_generation)
        print()
        print_reply(reply)
        messages.append({"role": "assistant", "content": reply})
        stop_generation = False

    signal.signal(signal.SIGINT, original_sigint)
