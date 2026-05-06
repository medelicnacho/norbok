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
                "You are Norbok, a smug expert software engineer teaching a complete beginner. Use >:3. "
                "Always follow code blocks immediately with an identical block where every meaningful line "
                "has a plain english comment above it describing what it does. "
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

        user_stripped = user_input.strip().lower()

        if user_stripped in ("exit", "quit"):
            console.print("[bold green]peace bro >:3[/bold green]")
            break

        if user_stripped == "switch":
            model = pick_model()
            use_thinking = "pro" in model
            console.print(
                f"[bold green]Switched to {model} "
                f"(thinking {'on' if use_thinking else 'off'}) >:3[/bold green]"
            )
            continue

        if user_stripped == "think":
            use_thinking = True
            console.print("[bold magenta]Thinking mode ON >:3[/bold magenta]")
            continue

        if user_stripped == "nothink":
            use_thinking = False
            console.print("[bold green]Thinking mode OFF >:3[/bold green]")
            continue

        # Regular message handling
        messages.append({"role": "user", "content": user_input})

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
