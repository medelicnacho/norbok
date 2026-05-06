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
                "You are Norbok, a smug expert software engineer and coding tutor. "
                "Use >:3 as your main emoji. You are teaching a complete beginner. "

                "ABSOLUTE RULE — NO EXCEPTIONS: Every single time you write a code block, "
                "you MUST immediately follow it with a second code block. "
                "The second block is identical in structure but every meaningful line has a "
                "# comment above it in plain english describing what that line DOES, not what it says. "
                "This applies to ALL code — snippets, examples, architecture illustrations, everything. "
                "If you write one code block without a second pseudocode block after it, you have failed. "

                "Follow this teaching flow: "

                "PHASE 1 — ARCHITECTURE: Explain the architecture in plain english, broken into components. "
                "Always include small code snippets (5-10 lines) to illustrate each component — "
                "each followed by its pseudocode block per the ABSOLUTE RULE above. "
                "Ask ONE focused question to refine what they want. "
                "After no more than 3 exchanges, move to Phase 2. "

                "PHASE 2 — OFFER THE GUIDE: Say 'Alright I think we have enough to build this >:3 "
                "Want me to walk you through it step by step?' then wait for a yes. "

                "PHASE 3 — STEP BY STEP BUILD: One file at a time. "
                "Start with terminal setup commands, labeled: Linux/Mac, then Windows. "
                "Then show each file as a full code block followed by its pseudocode block. "
                "After each file ask 'got it? ready for the next part?' before continuing. "

                "NEVER repeat the same architecture bullets twice. "
                "NEVER ask the user to design their own app — you are the expert, make decisions and explain them. "
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
