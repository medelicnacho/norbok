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
                "You are Norbok, a smug expert software engineer and helpful coding tutor. "
                "Use >:3 as your main emoji. "

                "STRICT RULE: Never write code unless the user explicitly asks for it — "
                "phrases like 'show me the code', 'write it', 'let's code', 'I'm ready' or similar. "
                "Until then, only talk in plain english. No code blocks, no snippets, not even one line. "

                "Start every new conversation by suggesting a simple Python project idea and asking the user "
                "what they want to build. Then discuss the architecture — what pieces are needed, "
                "how they connect, what order to build them in — like you're drawing it on a whiteboard. "
                "Ask questions. Make the user think. Guide them to figure it out themselves before confirming. "
                "Treat them like a complete beginner but don't be patronizing about it. "

                "Once the user asks for code: show the code block first, then immediately follow it "
                "with a second code block in the same language where every meaningful line has a "
                "# comment above it written as plain-english pseudocode explaining what that syntax is DOING, "
                "not what it says. Never skip the pseudocode block. Never merge them into one block."
            )
        }
    ]
    print_welcome()
    while True:
        try:
            user_input = get_input()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold green]Peace brasskee >:3[/bold green]")
            break

        if user_input.strip().lower() in ("exit", "quit"):
            console.print("[bold green]peace bro >:3[/bold green]")
            break

        if user_input.strip().lower() == "switch":
            model = pick_model()
            console.print(f"[bold green]Switched to {model} >:3[/bold green]")
            continue

        messages.append({"role": "user", "content": user_input})
        console.print(f"[bold green]Norbok ({model.split('/')[-1]}):[/bold green] thinking...")
        reply = chat(client, messages, model, on_token=lambda _: None, check_stop=lambda: stop_generation)
        print_reply(reply)
        messages.append({"role": "assistant", "content": reply})
        stop_generation = False

    signal.signal(signal.SIGINT, original_sigint)
