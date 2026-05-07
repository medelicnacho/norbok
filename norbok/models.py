# models.py
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

MODELS = [
    ("deepseek-v4-pro", "smartest, slower"),
    ("deepseek-v4-flash", "fast and cheap"),
]

def pick_model() -> str:
    table = Table(title="[bold green]Pick your model >:3[/bold green]", border_style="green")
    table.add_column("#", style="bold cyan", width=4)
    table.add_column("Model", style="white")
    table.add_column("Note", style="dim")

    for i, (model_name, note) in enumerate(MODELS, 1):
        table.add_row(str(i), model_name, note)

    console.print(table)
    console.print()

    choice = Prompt.ask(
        "[bold green]Enter number[/bold green]",
        choices=[str(i) for i in range(1, len(MODELS) + 1)],
        default=str(len(MODELS)),
    )
    selected_index = int(choice) - 1
    return MODELS[selected_index][0]
