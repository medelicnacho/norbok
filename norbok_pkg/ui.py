from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

def print_welcome():
    console.print(Panel("Norbok is ready to teach >:3", border_style="green"))

def print_reply(reply):
    console.print(Panel(Markdown(reply), title="Norbok", border_style="green"))

def get_input():
    return console.input("[bold green]student:[/bold green] ")