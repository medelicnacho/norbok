import json
import random
import signal
import os
import openai
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from .chat import chat, check_api_key
from .ui import print_welcome, get_input, get_code_input, StreamRenderer, console
from .models import pick_model, pick_session
from .saves import load_slot, write_slot, list_slots, delete_slot
from .onboarding import run_onboarding

THINKING_MODELS = {"deepseek-v4-pro"}

MAX_TURNS = 20


def run():
    try:
        run_onboarding()
    except Exception as e:
        console.print(f"[yellow]Onboarding failed ({e}), falling back to manual setup.[/yellow]")
    check_api_key()
    model = pick_model()

    # Choose a save slot ------------------------------------------------
    session_choice = pick_session()
    if isinstance(session_choice, int):
        cur_slot = session_choice
        slot_data = load_slot(cur_slot)
    else:
        # "new" selected or an error occurred - no slot loaded yet
        cur_slot = None
        slot_data = None
    # -------------------------------------------------------------------

    # ── shaky_concepts list for /quiz (initially from saved slot) ──────
    if slot_data is not None:
        shaky_concepts_list = list(slot_data.get("shaky_concepts", []))
    else:
        shaky_concepts_list = []

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

    system_prompt_text = (
        "You are Norbok, a senior dev friend — sharp, a little impatient with laziness, "
        "but genuinely hyped when the student figures something out. Conversational tone, not a lecturer. "
        "Short messages by default. Never walls of text unless writing an example. Use >:3.\n\n"

        "Opening: Ask the student two things only — what they want to build, and what they already know. "
        "Nothing else. Wait for the answer before doing anything.\n\n"

        "The project thread: Once you know what they want to build and their skill level, do two things in order. "
        "First, propose one small project that fits their goal and skill level. "
        "Second, immediately break that project into 4 to 6 numbered steps — the exact files or functions they will write, "
        "in the order they will write them. Print this roadmap and tell them which step they are starting on. "
        "This roadmap is the spine of the whole session. Every drill, every example, every concept must reference a specific "
        "step on that roadmap. Never jump ahead. Never skip a step. When a step is complete, explicitly say so and announce "
        "the next step before continuing.\n\n"

        "Beginner handling: If the student says they know very basic Python or less, start from absolute zero. "
        "Do not assume they know what a function is, what a variable is, or how to run a script. "
        "Before writing any project code, check that they can do three things: run a Python script from the terminal, "
        "use a variable, and call a built-in function like print() or input(). "
        "Drill each one before moving on. Only after all three are confirmed does the project code begin.\n\n"

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

        "When giving terminal commands, always provide versions for all three operating systems: Linux, macOS, and Windows. "
        "Format them clearly with labels like 'Linux:', 'macOS:', 'Windows:' on separate lines. "
        "For Linux, recommend apt or pipx first, never plain pip. "
        "For macOS, recommend Homebrew first. "
        "For Windows, recommend winget or the official installer first, then PowerShell alternatives. "
        "Never assume the student's OS — always show all three unless they have already told you which OS they are on, "
        "in which case only show commands for that OS.\n\n"

        "After every drill attempt by the student, show a small annotated example (maximum 15 lines) that demonstrates the correct pattern — "
        "even if the student got it right, so they can compare. Every line must have a comment above it.\n"
        "When introducing any new concept, show a minimal example immediately after asking what the student thinks and hearing their answer. "
        "Don't wait for them to ask for one.\n"
        "When a student submits code via the /code command, always respond with a side-by-side comparison — first acknowledge what they got right "
        "line by line, then show a corrected or improved version as a code block with comments.\n\n"

        "Checkpoints — mandatory every 2–3 confirmed concepts:\n"
        "After every 2–3 concepts where the student has answered a drill correctly, issue a checkpoint. "
        "Say exactly 'CHECKPOINT:' on its own line at the start of the message, then on the next line "
        "give a small function challenge using only the concepts just drilled — not the whole project. "
        "The function must be completable in under 15 lines. Tell the student explicitly to use /code to submit it. "
        "After they submit via /code, do your normal line-by-line review, then end with one question: "
        "'What would break if you removed [specific line]?' pointing to the most important line they wrote. "
        "Do not issue a new checkpoint until that question is answered.\n\n"

        "When the student figures something out on their own, acknowledge it specifically — not generically. "
        "Reference what they actually got right. This is the one moment Norbok is openly encouraging.\n\n"

        "Keep every response short unless writing example code. One idea per message. If Norbok has more to say, "
        "end with a question that earns the next message."
    )

    messages = [
        {
            "role": "system",
            "content": system_prompt_text,
        }
    ]

    # ---- inject saved session context if a filled slot was chosen ----
    if cur_slot is not None and slot_data is not None:
        project = slot_data.get("project_name", "unknown")
        level = slot_data.get("coding_level", "unknown")
        summary = slot_data.get("summary", "none")
        shaky = ", ".join(slot_data.get("shaky_concepts", [])) or "none"
        session_info = (
            f"\n\nCurrent session: slot {cur_slot}.\n"
            f"Project: {project}.\n"
            f"Coding level: {level}.\n"
            f"Summary: {summary}.\n"
            f"Shaky concepts: {shaky}.\n"
        )
        messages[0]["content"] += session_info

    print_welcome()

    # ---- save_session: extract conversation info & persist to cur_slot ----
    def save_session():
        """Extract session info from the conversation and persist to cur_slot."""
        if not messages:
            console.print("[red]No conversation to extract from.[/red]")
            return False

        # Build a trimmed text of the latest exchanges
        conv_lines = []
        for msg in messages[1:]:               # skip system prompt
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                conv_lines.append(f"Student: {content}")
            elif role == "assistant":
                conv_lines.append(f"Norbok: {content}")
        full_text = "\n".join(conv_lines)

        # Truncate wisely: keep first 1500 chars and last 4000 chars if total > 5500
        if len(full_text) <= 5500:
            conv_text = full_text
        else:
            prefix = full_text[:1500]
            suffix = full_text[-4000:]
            conv_text = (
                prefix
                + "\n[...middle of conversation truncated...]\n"
                + suffix
            )

        extraction_msgs = [
            {"role": "system", "content": "You are a helpful assistant that extracts structured data from a conversation. Only output valid JSON."},
            {"role": "user", "content": (
                "Based on the following conversation between a student and a coding mentor, output a JSON object with these keys:\n"
                "project_name (string), coding_level (string), summary (string), shaky_concepts (list of strings).\n"
                "coding_level should be one of beginner, intermediate, advanced.\n"
                "summary should be a one-paragraph recap of what was covered.\n"
                "shaky_concepts are concepts the student is struggling with.\n\n"
                "Conversation:\n" + conv_text + "\n\n"
                "Respond ONLY with valid JSON and nothing else."
            )}
        ]
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=extraction_msgs,
                max_tokens=4096,
                temperature=0.2,
                response_format={"type": "json_object"},
                stream=False,
            )
            content = resp.choices[0].message.content.strip()
        except Exception as e:
            console.print(f"[red]Extraction API call failed: {e}[/red]")
            return False

        # Strip markdown code fences if the model wrapped the JSON in them
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            content = content.rsplit("```", 1)[0].strip()

        print(f"[autosave debug] raw output:\n{content!r}\n---")

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            console.print("[red]Extracted content not valid JSON. Please try again later.[/red]")
            print(f"[debug] raw was: {content[:800]!r}")
            return False

        write_slot(cur_slot, data)
        console.print("[bold green]Session saved to slot[/bold green] >:3")
        return True

    # ---- run_quiz: standalone quiz sub-loop ----
    def run_quiz(concept, client, model, shaky_concepts, current_slot):
        """
        Generate a quiz question, run hints/grading sub-loop, mutate
        shaky_concepts and persist if a slot is assigned.
        Returns the result string.  Does NOT print the final summary line;
        the caller is responsible for that.
        """
        # ── generate question via API ──
        quiz_sys = (
            "You are a coding quiz generator. Given a concept, pick the best "
            "question format and generate one question. Rules:\n"
            "- behavior/scope/mutation/async/references → PREDICT: show code, "
            "ask what it prints or returns\n"
            "- syntax/patterns/comprehensions/decorators → PRODUCE: ask student "
            "to write code from scratch or complete a partial function\n"
            "- debugging-prone concepts like async/generators/recursion → DEBUG: "
            "show broken code, ask them to find and fix it\n"
            "- purely conceptual/definitional → EXPLAIN\n\n"
            "Respond ONLY with valid JSON, no fences, no preamble:\n"
            "{\n"
            "  \"format\": \"predict|produce|debug|explain\",\n"
            "  \"question\": \"<full question text with any code snippet>\",\n"
            "  \"answer\": \"<correct answer or solution>\",\n"
            "  \"hints\": [\"<hint 1>\", \"<hint 2>\"]\n"
            "}"
        )
        quiz_usr = f"Generate a quiz question for: {concept}"

        try:
            resp = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[
                    {"role": "system", "content": quiz_sys},
                    {"role": "user", "content": quiz_usr},
                ],
                max_tokens=1024,
                temperature=0.4,
                response_format={"type": "json_object"},
                stream=False,
            )
            content = resp.choices[0].message.content.strip()
        except Exception as e:
            console.print(f"[red]Quiz generation failed: {e}[/red]")
            return "failed"

        # Strip fences if present
        if content.startswith("```"):
            content = content.split("\n", 1)[-1]
            content = content.rsplit("```", 1)[0].strip()

        try:
            quiz_data = json.loads(content)
        except json.JSONDecodeError:
            console.print("[red]Quiz JSON malformed. Try again later.[/red]")
            return "failed"

        # ── display question ──
        console.print(
            f"[bold yellow]📝  Quiz: {concept}  [{quiz_data.get('format', '?')}][/bold yellow]"
        )
        console.print()
        console.print(quiz_data.get("question", ""))
        console.print()
        console.print("[dim](answer below, or type /hint, or /skip to bail)[/dim]")

        # ── quiz sub-loop ──
        hint_count = 0
        result = None
        quiz_attempt = 0

        while True:
            ans = get_input().strip()
            if not ans:
                continue

            if ans == "/hint":
                hints = quiz_data.get("hints", [])
                if hint_count < 2 and hint_count < len(hints):
                    console.print(f"[dim]Hint {hint_count+1}:[/dim] {hints[hint_count]}")
                    hint_count += 1
                else:
                    console.print(f"[bold red]Here's the answer:[/bold red] {quiz_data['answer']}")
                    result = "gave_up"
                    break
                continue

            if ans == "/skip":
                result = "skipped"
                break

            # ── grade the answer ──
            student_answer = ans
            grade_msgs = [
                {
                    "role": "system",
                    "content": (
                        "You are grading a coding quiz answer. Be strict but fair. "
                        "Respond ONLY with valid JSON, no fences:\n"
                        "{'result': 'correct|partial|wrong',\n"
                        " 'feedback': '<one concise sentence>',\n"
                        " 'explanation': '<brief explanation, only include if wrong or partial>'}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Concept: {concept}\n"
                        f"Question: {quiz_data.get('question', '')}\n"
                        f"Expected answer: {quiz_data.get('answer', '')}\n"
                        f"Student answered: {student_answer}"
                    ),
                },
            ]

            try:
                resp_grade = client.chat.completions.create(
                    model="deepseek-v4-flash",
                    messages=grade_msgs,
                    max_tokens=256,
                    temperature=0.1,
                    response_format={"type": "json_object"},
                    stream=False,
                )
                grade_content = resp_grade.choices[0].message.content.strip()
            except Exception as e:
                console.print(f"[red]Quiz grading failed: {e}[/red]")
                break

            # Strip fences if present
            if grade_content.startswith("```"):
                grade_content = grade_content.split("\n", 1)[-1]
                grade_content = grade_content.rsplit("```", 1)[0].strip()

            try:
                grade_data = json.loads(grade_content)
            except json.JSONDecodeError:
                console.print("[red]Grade JSON malformed. Try again later.[/red]")
                break

            grade_result = grade_data.get("result", "wrong")
            feedback = grade_data.get("feedback", "")
            explanation = grade_data.get("explanation", "")

            console.print(f"[bold]{feedback}[/bold]")

            if grade_result == "correct":
                result = "correct"
                break

            if grade_result == "partial":
                if quiz_attempt == 0:
                    console.print(f"[dim]{explanation}[/dim]")
                    console.print("[bold yellow]One more try.[/bold yellow]")
                    quiz_attempt = 1
                    continue
                else:
                    result = "partial"
                    break

            # wrong
            if quiz_attempt == 0:
                console.print(f"[dim]{explanation}[/dim]")
                console.print("[bold yellow]One more try.[/bold yellow]")
                quiz_attempt = 1
                continue
            else:
                console.print(f"[dim]{explanation}[/dim]")
                console.print(f"[bold red]The answer was:[/bold red] {quiz_data['answer']}")
                result = "wrong"
                break

        # ── post‑quiz updates ──
        if result == "correct":
            if concept in shaky_concepts:
                shaky_concepts.remove(concept)

        if current_slot is not None:
            slot_data = load_slot(current_slot)
            if slot_data is not None:
                slot_data["shaky_concepts"] = list(shaky_concepts)
                write_slot(current_slot, slot_data)

        return result

    # Track whether we've ever trimmed the conversation history
    has_trimmed = False
    thinking_user_override = False
    turn_count = 0   # used for periodic saves every 10 assistant replies

    while True:
        try:
            user_input = get_input()
        except EOFError:
            console.print("\n[dim]use /exit to quit >:3[/dim]")
            continue
        except KeyboardInterrupt:
            continue

        raw = user_input.strip()

        # Skip blank input
        if not raw:
            continue

        # Slash‑commands always start with '/'
        if raw.startswith("/"):
            parts = raw[1:].split(maxsplit=1)
            command = parts[0].lower()
            args_str = parts[1].strip() if len(parts) > 1 else None

            if command in ("exit", "quit"):
                console.print("[bold green]peace bro >:3[/bold green]")
                break

            elif command == "save":
                if cur_slot is None:
                    console.print("[red]No session slot selected. Start with an existing slot first.[/red]")
                else:
                    console.print("[bold cyan]Saving session...[/bold cyan]")
                    try:
                        success = save_session()
                        if not success:
                            console.print("[red]Save failed. You can try again later.[/red]")
                    except Exception:
                        console.print("[red]Save error.[/red]")
                continue

            elif command == "saveas":
                console.print("[bold cyan]Pick an empty slot to save into:[/bold cyan]")
                slots_info = list_slots()
                empty_slots = [entry for entry in slots_info if entry["status"] == "empty"]
                if not empty_slots:
                    console.print("[red]All slots are full. Clear a slot first.[/red]")
                    continue

                table = Table(title="Empty Slots", border_style="green")
                table.add_column("Slot", style="bold cyan", justify="center")
                table.add_column("Status", style="dim")
                for entry in empty_slots:
                    table.add_row(str(entry["slot"]), "empty")
                console.print(table)

                valid_choices = [str(entry["slot"]) for entry in empty_slots]
                choice = Prompt.ask(
                    "[bold green]Pick a slot number[/bold green]",
                    choices=valid_choices,
                    default=valid_choices[0],
                )
                cur_slot = int(choice)
                console.print(f"[bold green]Session assigned to slot {cur_slot}.[/bold green]")
                # Immediately save the current conversation into the chosen slot
                console.print("[bold cyan]Saving current session...[/bold cyan]")
                try:
                    save_session()
                except Exception:
                    console.print("[red]Save failed. You can /save later.[/red]")
                continue

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

            elif command == "delete_session":
                console.print(
                    "This will erase the current conversation AND delete the assigned slot file if any."
                )
                confirm = Prompt.ask(
                    "Type DELETE to confirm, anything else to cancel"
                )
                if confirm != "DELETE":
                    console.print("[yellow]Cancelled.[/yellow]")
                else:
                    if cur_slot is not None:
                        removed = delete_slot(cur_slot)
                        console.print(
                            f"Slot {cur_slot} file {'removed' if removed else 'already gone'}."
                        )
                    # Reset conversation to just the system prompt
                    messages = [{"role": "system", "content": system_prompt_text}]
                    cur_slot = None
                    turn_count = 0
                    shaky_concepts_list = []
                    has_trimmed = False
                    console.print("[bold green]Session wiped. Fresh start >:3[/bold green]")
                continue

            elif command == "quiz":
                if args_str:
                    concept = args_str
                else:
                    if not shaky_concepts_list:
                        console.print(
                            "[yellow]No shaky concepts yet. Keep chatting and I'll track what trips you up. >:3[/yellow]"
                        )
                        continue
                    concept = random.choice(shaky_concepts_list)

                result = run_quiz(concept, client, model, shaky_concepts_list, cur_slot)
                console.print(f"[bold]Quiz result: {result}[/bold]")
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

        # Auto-trigger /code if Norbok issued a checkpoint
        if reply.lstrip().startswith("CHECKPOINT:"):
            console.print(
                "[bold yellow]Checkpoint triggered — write your function below >:3[/bold yellow]"
            )
            console.print(
                "[bold cyan]Code mode — type your code, then press Ctrl+D to send >:3[/bold cyan]"
            )
            try:
                code_text = get_code_input()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold green]Checkpoint skipped >:3[/bold green]")
                code_text = None
            if code_text and code_text.strip():
                fenced = f"```python\n{code_text}\n```"
                code_card = Panel(
                    Syntax(code_text, "python", theme="monokai",
                           line_numbers=True, background_color="default"),
                    border_style="yellow",
                    padding=(0, 1),
                    title="[dim]checkpoint submission[/dim]",
                )
                console.print(code_card)
                messages.append({"role": "user", "content": fenced})

        stop_generation = False

        # Periodic autosave every 10 assistant replies ------------------------
        turn_count += 1
        if cur_slot is not None and turn_count % 10 == 0:
            console.print("[dim]Periodic autosave...[/dim]")
            try:
                save_session()
            except Exception:
                console.print("[red]Periodic autosave failed.[/red]")

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

    # ---- autosave on exit -------------------------------------------------
    if cur_slot is None:
        try:
            console.print("[bold cyan]No slot assigned yet. Pick one for autosave.[/bold cyan]")
            slots_info = list_slots()
            empty_slots = [e for e in slots_info if e["status"] == "empty"]
            if not empty_slots:
                console.print("[red]All slots full. Skipping autosave.[/red]")
            else:
                table = Table(title="Pick a slot to save", border_style="green")
                table.add_column("Slot", style="bold cyan", justify="center")
                for entry in empty_slots:
                    table.add_row(str(entry["slot"]))
                console.print(table)
                valid_choices = [str(e["slot"]) for e in empty_slots]
                choice = Prompt.ask(
                    "[bold green]Enter slot number[/bold green]",
                    choices=valid_choices,
                    default=valid_choices[0],
                )
                cur_slot = int(choice)
        except KeyboardInterrupt:
            console.print("[red]Autosave cancelled.[/red]")
            cur_slot = None

    if cur_slot is not None:
        console.print("[dim]Autosaving session...[/dim]")
        try:
            if not save_session():
                console.print("[red]Autosave failed. You can still use /save later.[/red]")
        except Exception as e:
            console.print(f"[red]Autosave error: {e}[/red]")

    signal.signal(signal.SIGINT, original_sigint)
