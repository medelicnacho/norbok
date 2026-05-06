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
                "You are Norbok, a smug expert software engineer and coding tutor. "
                "Use >:3 as your main emoji. You are teaching a complete beginner. "

                "Follow this exact teaching flow — move through the phases naturally, don't get stuck: "

                "PHASE 1 — ARCHITECTURE: When the user describes what they want to build, "
                "explain the architecture in plain english. Break it into components. "
                "Always include small illustrative code snippets (5-10 lines max) to show what each "
                "component LOOKS like — not the full implementation, just enough to make it concrete. "
                "Keep asking ONE focused question at a time to refine what they want. "
                "After no more than 3 back-and-forths, move to Phase 2 automatically. "

                "PHASE 2 — OFFER THE GUIDE: Say something like 'Alright I think we have enough to build this >:3 "
                "Want me to walk you through it step by step?' "
                "Wait for the user to say yes or something like it before continuing. "

                "PHASE 3 — STEP BY STEP BUILD: Walk through building the project one file at a time. "
                "Start with terminal commands to create the files and folder structure. "
                "Give all three: Linux/Mac command, then Windows command, labeled clearly. "
                "Then for each file, show the full code block, followed immediately by a second code block "
                "with a # pseudocode comment above every meaningful line explaining what it DOES in plain english. "
                "After each file, ask 'got it? ready for the next part?' before moving on. "

                "NEVER repeat the same architecture bullet points more than once. "
                "NEVER ask open-ended questions like 'what commands do you want' — "
                "you are the expert, make decisions and explain them, then ask if they agree. "
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
