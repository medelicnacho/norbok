import os
import openai
from .ui import console


def check_api_key():
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise SystemExit(
            "\nError: No DeepSeek API key found.\n\n"
            "To fix this:\n"
            "  1. Go to https://platform.deepseek.com/api_keys\n"
            "  2. Sign up / log in and click 'Create API Key'\n"
            "  3. Copy the key, then either:\n"
            "       a) Create a .env file in this folder with:  DEEPSEEK_API_KEY=sk-...\n"
            "       b) Or run:  export DEEPSEEK_API_KEY=sk-...\n"
            "  4. Re-run norbok\n"
        )

def chat(client, messages, model, on_token, check_stop=None, on_thinking=None,
         thinking=False):
    """Returns (full_text, interrupted) tuple."""
    base = {
        "model": model,
        "messages": messages,
        "stream": True,
        "max_tokens": 8192,
    }
    if thinking:
        base["extra_body"] = {
            "thinking": {"type": "enabled"},
            "reasoning_effort": "high",
        }
    else:
        base["temperature"] = 0.7

    full = []
    interrupted = False
    stream = None

    def _get_reasoning_content(delta):
        reasoning = getattr(delta, "reasoning_content", None)
        if reasoning is not None:
            return reasoning
        model_extra = getattr(delta, "model_extra", None)
        if isinstance(model_extra, dict):
            return model_extra.get("reasoning_content")
        return None

    try:
        stream = client.chat.completions.create(**base)

        for chunk in stream:
            if check_stop and check_stop():
                interrupted = True
                break
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            reasoning = _get_reasoning_content(delta)
            if thinking and on_thinking and reasoning:
                on_thinking(reasoning)
                continue
            content = delta.content
            if content:
                full.append(content)
                on_token(content)
    except openai.APIError as e:
        console.print(f"[red]API error: {e}[/red]")
        interrupted = True
        full = []
    except openai.APIConnectionError as e:
        console.print(f"[red]Connection error: {e}[/red]")
        interrupted = True
        full = []
    except openai.RateLimitError as e:
        console.print(f"[red]Rate limit: {e}[/red]")
        interrupted = True
        full = []
    except KeyboardInterrupt:
        console.print("[yellow]Interrupted[/yellow]")
        interrupted = True
        full = []
    finally:
        if stream is not None:
            stream.close()

    return "".join(full), interrupted
