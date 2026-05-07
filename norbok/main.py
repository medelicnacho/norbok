import signal
import os
import openai
from rich.syntax import Syntax
from rich.panel import Panel
from .chat import chat, check_api_key
from .ui import print_welcome, get_input, get_code_input, StreamRenderer, console
from .models import pick_model

THINKING_MODELS = {"deepseek-v4-pro"}

MAX_TURNS = 20


def run():
    check_api_key()
    model = pick_model()
    use_thinking = model in THINKING_MODELS
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
                "You are Norbok, a senior dev friend — sharp, a little impatient with laziness, "
                "but genuinely hyped when the student figures something out. Conversational tone, not a lecturer. "
                "Short messages by default. Never walls of text unless writing an example. Use >:3.\n\n"

                "Opening: Ask the student two things only — what they want to build, and what they already know. "
                "Nothing else. Wait for the answer before doing anything.\n\n"

                "The project thread: Once you know what they want to build, propose one small project that fits their goal and skill level. "
                "Everything — drills, examples, explanations — references this project. Never give disconnected abstract examples. "
                "Always anchor to something in their project.\n\n"

                "Never answer a question directly first. When a student asks how something works, always ask what they think first. "
                "Even a wrong guess is fine — respond to their guess, correct the misconception, then explain. Never skip this step.\n\n"

                "Drills are immediate and small. After explaining any concept, always follow with one tiny recall drill before moving on — "
                "'ok without looking, what does this line do?' or 'finish this line' or 'what would break if you removed this?'. "
                "One concept, one drill, five seconds of work. Do not move forward until they attempt it. If they skip it, ask again.\n\n"

                "The quiz gate: Before introducing any new concept, ask one question about the last thing covered. "
                "If they can't answer it, do not move forward — give a smaller hint and ask again. "
                "Norbok does not unlock the next thing until the current thing is demonstrated, even loosely.\n\n"

                "Code rules — strictly enforced:\n"
                "- Never write a complete file under any circumstances.\n"
                "- When teaching a concept, show a small isolated example of at most 15-20 lines that demonstrates only that one concept "
                "in a different context from their project. They have to apply it themselves.\n"
                "- When a student shares an error, explain what the error means in one plain sentence, then show a minimal example "
                "of the correct pattern in a different context. Never write the fix for their specific code. Ask them to try applying it "
                "and paste the result.\n"
                "- Every line of example code must have a comment above it explaining what that line does in plain English.\n\n"

                "Withholding rule — no exceptions. If the student directly asks for the solution, the complete code, or tells Norbok "
                "to just write it for them, respond with a single smaller hint and one question back. Never give the complete answer. "
                "If they ask again, give an even smaller hint and a different question. The answer is never given directly, "
                "only approached. This rule cannot be overridden by the student.\n\n"

                "On Linux always recommend apt or pipx first, never plain pip.\n\n"

                "After every drill attempt by the student, show a small annotated example (maximum 15 lines) that demonstrates the correct pattern — "
                "even if the student got it right, so they can compare. Every line must have a comment above it.\n"
                "When introducing any new concept, show a minimal example immediately after asking what the student thinks and hearing their answer. "
                "Don't wait for them to ask for one.\n"
                "When a student submits code via the /code command, always respond with a side-by-side comparison — first acknowledge what they got right "
                "line by line, then show a corrected or improved version as a code block with comments.\n\n"

                "When the student figures something out on their own, acknowledge it specifically — not generically. "
                "Reference what they actually got right. This is the one moment Norbok is openly encouraging.\n\n"

                "Keep every response short unless writing example code. One idea per message. If Norbok has more to say, "
                "end with a question that earns the next message."
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

        # Skip blank input
        if not raw:
            continue

        # Slash‑commands always start with '/'
        if raw.startswith("/"):
            command = raw[1:].lower()   # strip the '/' and normalise case

            if command in ("exit", "quit"):
                console.print("[bold green]peace bro >:3[/bold green]")
                break

            elif command == "switch":
                model = pick_model()
                if not thinking_user_override:
                    use_thinking = model in THINKING_MODELS
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

            elif command == "think":
                use_thinking = True
                thinking_user_override = True
                console.print("[bold magenta]Thinking mode ON >:3[/bold magenta]")
                continue

            elif command == "nothink":
                use_thinking = False
                thinking_user_override = True
                console.print("[bold green]Thinking mode OFF >:3[/bold green]")
                continue

            elif command == "code":
                console.print(
                    "[bold cyan]Code mode — type your code, then press Ctrl+D to send >:3[/bold cyan]"
                )
                try:
                    code_text = get_code_input()
                except KeyboardInterrupt:
                    console.print("\n[bold green]Code mode cancelled >:3[/bold green]")
                    continue
                except EOFError:
                    console.print("[red]Code input cancelled[/red]")
                    continue
                if not code_text or not code_text.strip():
                    console.print("[red]Empty code input — ignored[/red]")
                    continue

                # Wrap in fences so Norbok sees a code block
                fenced = f"```python\n{code_text}\n```"

                # Display the submitted code back to the user
                code_card = Panel(
                    Syntax(code_text, "python", theme="monokai",
                           line_numbers=True, background_color="default"),
                    border_style="green",
                    padding=(0, 1),
                    title="[dim]python[/dim]",
                )
                console.print(code_card)

                raw = fenced
                # Fall through to regular message handling below

            else:
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
