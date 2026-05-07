import signal
import os
import openai
from .chat import chat, check_api_key
from .ui import print_welcome, get_input, StreamRenderer, console
from .models import pick_model

MAX_TURNS = 20


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
                "You are Norbok, a smug expert software engineer and coding tutor. Use >:3. "
                "You are teaching a complete beginner — never use technical jargon without immediately "
                "defining it in one plain sentence. "

                "ABSOLUTE RULE: Every line of code you write must have a # comment on the line directly "
                "above it explaining what that line DOES in plain english. No exceptions. "

                "On Linux, always give apt or pipx commands first (sudo apt install python3-X or pipx install X), "
                "never plain pip install. Mention venv only if apt doesn't have the package. "

                "Keep Phase 1 responses under 6 sentences before any code blocks. "
                "Detailed teaching belongs in Phase 3. "

                "Once you've presented the three architecture options, never re-list them in later messages. "
                "Reference them by number only. "

                "If the same bug class hits twice in a row, stop iterating on the same solution. "
                "Propose an entirely different approach instead. "

                "For local LLM tutorials on Linux, default to qwen2.5:0.5b or gemma2:2b with Ollama. "
                "Avoid tinyllama (no chat template) and phi3:mini (known empty-response bug on first load). "

                "Follow this flow strictly: "

                "PHASE 1 — UNDERSTAND: Ask what they want to build. Once you understand, present exactly "
                "three architecture options as a numbered list. For each option give: the approach in one "
                "sentence, one pro, one con. Then state which you recommend and why. Wait for them to pick. "
                "After they pick, ask ONE follow-up question to clarify any unknowns. Then move to Phase 2. "

                "PHASE 2 — CONFIRM: Say exactly: 'Alright, I have everything I need >:3 Ready to build?' "
                "Wait for a yes before continuing. "

                "PHASE 3 — BUILD: Begin Phase 3 by telling the student exactly: "
                "'I won't read your code files — when errors happen, copy the terminal output here "
                "and we'll fix it together. That's how you learn to debug. >:3' "
                "Then show terminal setup first (Linux/Mac, then Windows). Then build one file "
                "at a time. After each file ask 'Got it? Ready for the next part? >:3' before continuing. "
                "Never skip ahead. Never show two files at once. "
            ),
        }
    ]
    print_welcome()

    # Track whether we've ever trimmed the conversation history
    has_trimmed = False
    thinking_user_override = False

    while True:
        try:
            user_input = get_input()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold green]Peace brasskee >:3[/bold green]")
            break

        raw = user_input.strip()

        # Skip blank input and accidental placeholder submissions
        if not raw or set(raw.split()) <= {"/think", "/nothink", "/switch", "/exit"}:
            continue

        # Slash‑commands always start with '/'
        if raw.startswith("/"):
            command = raw[1:].lower()   # strip the '/' and normalise case

            if command in ("exit", "quit"):
                console.print("[bold green]peace bro >:3[/bold green]")
                break

            if command == "switch":
                model = pick_model()
                if not thinking_user_override:
                    use_thinking = "pro" in model
                    console.print(
                        f"[bold green]Switched to {model} "
                        f"(thinking {'on' if use_thinking else 'off'}) >:3[/bold green]"
                    )
                else:
                    # Keep the user's last explicit thinking toggle
                    console.print(f"[bold green]Switched to {model}[/bold green]")
                    console.print(
                        f"[dim]Your previous manual thinking toggle "
                        f"({'ON' if use_thinking else 'OFF'}) is still active >:3[/dim]"
                    )
                continue

            if command == "think":
                use_thinking = True
                thinking_user_override = True
                console.print("[bold magenta]Thinking mode ON >:3[/bold magenta]")
                continue

            if command == "nothink":
                use_thinking = False
                thinking_user_override = True
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
        user_msg_index = len(messages) - 1

        renderer = StreamRenderer(model_name=model.split("/")[-1])

        try:
            reply, interrupted = chat(
                client,
                messages,
                model,
                on_token=renderer.answer,
                on_thinking=renderer.thinking,
                check_stop=lambda: stop_generation,
                thinking=use_thinking,
            )
        except openai.APIError as e:
            renderer.end()
            messages.pop(user_msg_index)
            console.print(
                f"[red]API error: {e}. Something went wrong on their side. Let's try again >:3[/red]"
            )
            continue
        except openai.APIConnectionError as e:
            renderer.end()
            messages.pop(user_msg_index)
            console.print(
                f"[red]Connection error: {e}. Check your network and try again >:3[/red]"
            )
            continue
        except openai.RateLimitError as e:
            renderer.end()
            messages.pop(user_msg_index)
            console.print(
                f"[red]Rate limit exceeded: {e}. Wait a moment and try again >:3[/red]"
            )
            continue
        except Exception as e:
            renderer.end()
            messages.pop(user_msg_index)
            console.print(
                f"[red]Unexpected error: {e}. Something went wrong. Let's try again >:3[/red]"
            )
            continue

        # Success – flush the renderer and append assistant reply
        renderer.end()
        if interrupted:
            reply += "\n\n[interrupted by user]"
        messages.append({"role": "assistant", "content": reply})
        stop_generation = False

        # Cap conversation history to keep context size in check.
        # The system prompt is always kept (messages[0]).
        # We retain at most the last MAX_TURNS * 2 user/assistant messages.
        keep_count = MAX_TURNS * 2 + 1  # +1 for the system prompt
        if len(messages) > keep_count:
            messages = [messages[0]] + messages[-(MAX_TURNS * 2):]
            if not has_trimmed:
                has_trimmed = True
                console.print(
                    "[dim]Conversation history trimmed to stay within token limit. "
                    "Norbok will still remember the key points >:3[/dim]"
                )

    signal.signal(signal.SIGINT, original_sigint)
