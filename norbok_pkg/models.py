# models.py
import subprocess
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

console = Console()

MODELS = [
    "huihui_ai/qwen2.5-coder-abliterate:32b",
    "huihui_ai/qwen2.5-coder-abliterate:14b",
    "huihui_ai/qwen2.5-coder-abliterate:7b",
    "thirdeyeai/Qwen2.5-Coder-7B-Instruct-Uncensored",
    "r4c3r/qwen2.5-coder-3b-heretic",
    "huihui_ai/qwen2.5-coder-abliterate:1.5b",
    "huihui_ai/qwen2.5-coder-abliterate:0.5b",
]

def get_installed():
    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()[1:]  # skip header row
    return {line.split()[0] for line in lines if line.strip()}

def pick_model() -> str:
    installed = get_installed()

    table = Table(title="[bold green]Pick your weapon >:3[/bold green]", border_style="green")
    table.add_column("#",      style="bold cyan", width=4)
    table.add_column("Model",  style="white")
    table.add_column("Status", style="white")
    table.add_column("Note",   style="dim")

    SIZES = {
        "32b": "~20GB",  "14b": "~9GB", "7b": "~4.7GB",
        "3b":  "~2GB",   "1.5b": "~1GB", "0.5b": "~400MB",
    }

    for i, model in enumerate(MODELS, 1):
        tag   = model.split(":")[-1] if ":" in model else "7b"
        size  = SIZES.get(tag, "?")
        ready = installed.intersection({model, model.replace("/", "_")})  # ollama stores with _ sometimes
        status = "[green]● installed[/green]" if ready else "[yellow]○ not pulled[/yellow]"
        table.add_row(str(i), model, status, size)

    console.print(table)
    console.print()

    choice = Prompt.ask(
        "[bold green]Enter number[/bold green]",
        choices=[str(i) for i in range(1, len(MODELS) + 1)],
    )
    selected = MODELS[int(choice) - 1]

    # check again with fresh list in case naming differs
    if not get_installed().intersection({selected, selected.replace("/", "_")}):
        console.print(f"\n[bold yellow]Pulling {selected} — this may take a while >:3[/bold yellow]\n")
        # no capture_output so ollama's own progress bar renders directly
        result = subprocess.run(["ollama", "pull", selected])
        if result.returncode != 0:
            console.print("[bold red]Pull failed. Check the model name or your connection.[/bold red]")
            raise SystemExit(1)
        console.print(f"\n[bold green]Got it. Loading {selected} >:3[/bold green]\n")

    return selected