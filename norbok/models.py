# models.py
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from .saves import list_slots

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


def pick_session():
    """
    Display save slots and let the user pick one or start a new chat.

    Returns:
        "new"  - user chose to start a new chat
        int    - the slot number (1‑5) chosen
    """
    slots_info = list_slots()

    table = Table(
        title="[bold green]Save Slots[/bold green]",
        border_style="green",
    )
    table.add_column("Slot", style="bold cyan", justify="center")
    table.add_column("Project", style="white")

    for entry in slots_info:
        slot = entry["slot"]
        if entry["status"] == "filled":
            proj = entry["data"].get("project_name", "unknown")
        else:
            proj = "[dim](empty)[/dim]"
        table.add_row(str(slot), proj)

    # New chat option
    table.add_row("[bold]N[/bold]", "[bold green]New chat[/bold green]")

    console.print(table)
    console.print()

    choices = [str(i) for i in range(1, 6)] + ["n", "N"]
    choice = Prompt.ask(
        "[bold green]Choose a slot or N for new chat[/bold green]",
        choices=choices,
        default="N",
    )

    if choice.lower() == "n":
        return "new"
    return int(choice)
