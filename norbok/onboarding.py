import os
import tempfile
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich import box
from prompt_toolkit import prompt as ptk_prompt
from prompt_toolkit.styles import Style

console = Console()

PTK_STYLE = Style([("bold", "bold ansigreen")])

ENV_FILE = str(
    (Path.home() / ".config" / "norbok" / ".env")
    if os.name != "nt"
    else Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "norbok" / ".env"
)


def _ensure_data_dir():
    Path(ENV_FILE).parent.mkdir(parents=True, exist_ok=True)


def _load_env_file():
    """Load key=value pairs from .env into os.environ if the file exists."""
    if not os.path.isfile(ENV_FILE):
        return
    with open(ENV_FILE, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Strip a single matching pair of surrounding quotes (common .env convention)
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            os.environ.setdefault(key, value)


def _save_key_to_env_file(key: str):
    """Write or update DEEPSEEK_API_KEY in the local .env file."""
    _ensure_data_dir()

    lines = []
    replaced = False
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        new_lines = []
        for line in lines:
            if line.startswith("DEEPSEEK_API_KEY="):
                new_lines.append(f"DEEPSEEK_API_KEY={key}\n")
                replaced = True
            else:
                new_lines.append(line)
        lines = new_lines
    if not replaced:
        lines.append(f"DEEPSEEK_API_KEY={key}\n")

    parent_dir = Path(ENV_FILE).parent
    fd, tmp_path = tempfile.mkstemp(
        suffix=".env", prefix=".norbok", dir=str(parent_dir)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.writelines(lines)
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, ENV_FILE)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def run_onboarding():
    """
    Load .env, then show the setup guide if DEEPSEEK_API_KEY is still missing.
    Safe to call on every startup — exits immediately if the key is already set.
    """
    _load_env_file()

    if os.environ.get("DEEPSEEK_API_KEY"):
        return  # Already set, nothing to do

    console.print()
    console.print(
        Panel(
            "[bold green]Welcome to Norbok >:3[/bold green]\n\n"
            "Norbok needs a [bold]DeepSeek API key[/bold] to talk to the model.\n"
            "This is a one-time setup. It takes about 2 minutes.\n\n"
            "[dim]New accounts get [bold white]5 million free tokens[/bold white] — no credit card needed.\n"
            "That's enough for weeks of learning sessions.[/dim]",
            border_style="green",
            padding=(1, 2),
        )
    )
    console.print()
    console.print(Rule("[bold green]Setup steps[/bold green]", style="green"))
    console.print()

    console.print("[bold cyan]Step 1 — Get your API key[/bold cyan]")
    console.print("  Go to: [underline]https://platform.deepseek.com/api_keys[/underline]")
    console.print("  Sign up or log in, then click [bold]Create API Key[/bold].")
    console.print("  Copy the key — you won't be able to see it again after closing the page.")
    console.print()

    console.print("[bold cyan]Step 2 — Paste it below[/bold cyan]")
    console.print("  Norbok will save it to a [bold].env[/bold] file in this folder.")
    console.print("  You will not need to do this again.\n")

    while True:
        try:
            key = ptk_prompt(
                message=[("class:bold", "Paste your DeepSeek API key: ")],
                style=PTK_STYLE,
                is_password=True,
            ).strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[red]Setup cancelled. Run norbok again when you have your key.[/red]")
            raise SystemExit(0)

        if not key:
            console.print("[red]Key cannot be empty. Try again.[/red]")
            continue

        if not key.startswith("sk-"):
            console.print(
                "[yellow]That doesn't look like a DeepSeek key (should start with sk-). "
                "Double-check and try again.[/yellow]"
            )
            continue

        break

    _save_key_to_env_file(key)
    os.environ["DEEPSEEK_API_KEY"] = key

    console.print()
    console.print(
        Panel(
            "[bold green]Key saved to .env >:3[/bold green]\n\n"
            "Norbok is ready. Starting session...",
            border_style="green",
            padding=(1, 2),
        )
    )
    console.print()
