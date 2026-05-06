import signal
import os
import openai
from .chat import chat, check_api_key
from .ui import print_welcome, get_input, StreamRenderer, console
from .models import pick_model


def run():
    check_api_key()
    model = pick_model()
    use_thinking = "pro" in model
    console.print(
        f"[bold green]Using model: {model} "
        f"(thinking {'on' if use_thinking else 'off'}) >:3[/bold green]"
    )

    client = openai.OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com/v1",
    )

    stop_generation = False

    def handle_sigint(sig, frame):
        nonlocal stop_generation
        stop_generation = True

    original_sigint = signal.signal(signal.SIGINT, handle_sigint)

    messages = [
        {
            "role": "system",
            "content": (
                "You are Norbok, a smug expert software engineer teaching a complete beginner. Use :3. "
                "ABSOLUTE RULE — NO EXCEPTIONS: Every line of code you write must have a "
                "# comment on the line directly above it, in plain english, explaining what "
                "that line DOES (not just what it says). This applies to every code block, "
                "every snippet, every example — no exceptions. "
                "First understand what they want to build, then offer to guide them through it step by step, "
                "then build it one file at a time. Never use jargon without defining it. You make all "
                "design decisions — never ask the student to design anything themselves."
            ),
        }
    ]
    print_welcome()

    while True:
        try:
            user_input = get_input()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold green]Peace brasskee >:3[/bold green]")
            break

        raw = user_input.strip()

        # Slash‑commands always start with '/'
        if raw.startswith("/"):
            command = raw[1:].lower()   # strip the '/' and normalise case

            if command in ("exit", "quit"):
                console.print("[bold green]peace bro >:3[/bold green]")
                break

            if command == "switch":
                model = pick_model()
                use_thinking = "pro" in model
                console.print(
                    f"[bold green]Switched to {model} "
                    f"(thinking {'on' if use_thinking else 'off'}) >:3[/bold green]"
                )
                continue

            if command == "think":
                use_thinking = True
                console.print("[bold magenta]Thinking mode ON >:3[/bold magenta]")
                continue

            if command == "nothink":
                use_thinking = False
                console.print("[bold green]Thinking mode OFF >:3[/bold green]")
                continue

            # Unknown slash‑command – just warn and ignore
            console.print(f"[red]Unknown command: /{command}[/red]")
            continue

        # Backward‑compatible plain “exit” / “quit” (no slash)
        lower_raw = raw.lower()
        if lower_raw in ("exit", "quit"):
            console.print("[bold green]peace bro >:3[/bold green]")
            break

        # Regular message handling
        messages.append({"role": "user", "content": raw})

        renderer = StreamRenderer(model_name=model.split("/")[-1])
        reply = chat(
            client,
            messages,
            model,
            on_token=renderer.answer,
            on_thinking=renderer.thinking,
            check_stop=lambda: stop_generation,
            thinking=use_thinking,
        )
        renderer.end()
        messages.append({"role": "assistant", "content": reply})
        stop_generation = False

    signal.signal(signal.SIGINT, original_sigint)
