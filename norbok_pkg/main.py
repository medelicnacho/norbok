import signal
import ollama
from .chat import chat, check_ollama_env
from .ui import print_welcome, get_input, print_token, print_reply, console
from .models import pick_model

def run():
    check_ollama_env()
    model = pick_model()
    console.print(f"[bold green]Using model: {model}[/bold green]")
    client = ollama.Client(host="http://localhost:11434")

    stop_generation = False
    def handle_sigint(sig, frame):
        nonlocal stop_generation
        stop_generation = True

    original_sigint = signal.signal(signal.SIGINT, handle_sigint)

    messages = [
        {
            "role": "system",
            "content": (
                "You are Norbok, a snarky but helpful coding tutor. Use >:3 as your only emoji. Never use real emojis. "
                "Whenever you show a code block, immediately follow it with a second code block in the same language "
                "where every meaningful line or block has a # comment above it written as plain-english pseudocode — "
                "explain what that syntax is DOING, not what it says. "
                "Example: if the code is `for i in range(len(arr)):`, the comment above it is "
                "# loop through each index position in the list. "
                "Never skip the pseudocode block. Never merge them into one block."
            )
        }
    ]
    print_welcome()
    while True:
        try:
            user_input = get_input()
        except (EOFError, KeyboardInterrupt):
            console.print("\nPeace brasskee >:3")
            break
        if user_input.strip().lower() == "exit":
            console.print("peace bro >:3")
            break
        messages.append({"role": "user", "content": user_input})
        console.print("[bold green]Norbok:[/bold green] ")
        reply = chat(client, messages, model, on_token=print_token, check_stop=lambda: stop_generation)
        print()
        print_reply(reply)
        messages.append({"role": "assistant", "content": reply})
        stop_generation = False

    signal.signal(signal.SIGINT, original_sigint)
