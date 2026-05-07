from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from prompt_toolkit import prompt as ptk_prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

console = Console()


PTK_STYLE = Style([
    ("bold", "bold ansigreen"),
    ("placeholder", "#555555"),
])

COMMANDS = "/think  /nothink  /switch  /exit"


class StreamRenderer:
    def __init__(self, model_name=""):
        self.in_thinking = False
        self.in_answer = False
        self.thinking_streamed = False
        self.model_name = model_name

        # code‑card state
        self.in_code = False
        self.code_lang = ""
        self.code_buffer = []      # accumulated lines for the current code block
        self.text_buffer = ""      # buffered tokens between fences

    def thinking(self, token):
        if not self.in_thinking:
            console.print("\n🧠 thinking...", style="bold magenta")
            self.in_thinking = True
            self.thinking_streamed = True
        console.print(token, end="", markup=False, highlight=False, style="dim italic")

    def answer(self, token):
        if not self.in_answer:
            if self.thinking_streamed:
                console.print()
            header = f"Norbok ({self.model_name}) >:3" if self.model_name else "Norbok >:3"
            console.print(header, style="bold green")
            self.in_answer = True
        # Instead of printing directly, buffer and process code blocks
        self.text_buffer += token
        self._process()

    # ── code‑card detection and rendering ──────────────────────────────────
    def _process(self):
        while True:
            if not self.in_code:
                fence_pos = self.text_buffer.find("```")
                if fence_pos == -1:
                    # No fence yet → flush everything except the last 3 chars
                    # (they could become part of a ``` sequence in the next token)
                    if len(self.text_buffer) > 3:
                        to_print = self.text_buffer[:-3]
                        console.print(to_print, end="", markup=False, highlight=False)
                        self.text_buffer = self.text_buffer[-3:]
                    break

                # We found a potential opening fence
                before = self.text_buffer[:fence_pos]
                console.print(before, end="", markup=False, highlight=False)

                after_fence = self.text_buffer[fence_pos:]   # starts with ```
                nl = after_fence.find("\n", 3)
                if nl == -1:
                    # Whole line not yet ready → keep it and wait for more
                    self.text_buffer = after_fence
                    break

                # line is complete – extract language hint
                lang = after_fence[3:nl].strip()
                self.code_lang = lang
                self.code_buffer = []
                self.in_code = True
                # remaining text (including the newline) becomes code content
                self.text_buffer = after_fence[nl + 1:]
                # continue the while loop to immediately consume any code that already arrived
                continue

            else:
                # Inside a code block – look for the closing fence
                fence_pos = self.text_buffer.find("```")
                if fence_pos == -1:
                    # No closing fence yet → move everything except the last 3 chars
                    # into code_buffer (those 3 chars might be the start of ```)
                    if len(self.text_buffer) > 3:
                        to_move = self.text_buffer[:-3]
                        self.code_buffer.append(to_move)
                        self.text_buffer = self.text_buffer[-3:]
                    break

                # Closing fence found
                before_fence = self.text_buffer[:fence_pos]
                if before_fence:
                    self.code_buffer.append(before_fence)

                self._card()

                # Reset code‑block state and keep whatever came after the closing fence
                self.in_code = False
                self.code_lang = ""
                self.code_buffer = []
                self.text_buffer = self.text_buffer[fence_pos + 3:]
                # continue processing any further tokens (e.g. another code block)
                continue

    def _card(self):
        code = "".join(self.code_buffer)
        lang = self.code_lang or "text"
        console.print()   # blank line before the card
        console.print(
            Panel(
                Syntax(
                    code, lang, theme="monokai",
                    line_numbers=True, background_color="default",
                ),
                border_style="green",
                padding=(0, 1),
                title=f"[dim]{lang}[/dim]" if lang and lang != "text" else "",
            )
        )

    def end(self):
        # Flush any remaining text that never saw a fence
        if not self.in_code and self.text_buffer:
            console.print(self.text_buffer, end="", markup=False, highlight=False)
            self.text_buffer = ""

        # If we are still inside a code block at end, output what we have
        if self.in_code:
            if self.text_buffer:
                self.code_buffer.append(self.text_buffer)
                self.text_buffer = ""
            self._card()

        # Guarantee the output ends with a newline
        if self.text_buffer:
            console.print(self.text_buffer, end="", markup=False, highlight=False)
        console.print()


def print_welcome():
    console.print(Panel("Norbok is ready to teach >:3", border_style="green"))


def get_input():
    return ptk_prompt(
        message=[("class:bold", "student: ")],
        style=PTK_STYLE,
        placeholder=[("class:placeholder", COMMANDS)],
    )
