from rich.console import Console
from rich.panel import Panel

console = Console()


class StreamRenderer:
    def __init__(self, model_name=""):
        self.in_thinking = False
        self.in_answer = False
        self.thinking_streamed = False
        self.model_name = model_name

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
        console.print(token, end="", markup=False, highlight=False)

    def end(self):
        console.print()


def print_welcome():
    console.print(Panel("Norbok is ready to teach >:3", border_style="green"))


def get_input():
    return console.input("[bold green]student:[/bold green] ")
