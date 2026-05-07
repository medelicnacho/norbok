import os
import openai


def check_api_key():
    if not os.environ.get("DEEPSEEK_API_KEY"):
        raise SystemExit("Error: DEEPSEEK_API_KEY environment variable not set.")


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
        base.update(
            extra_body={"thinking": {"type": "enabled"}},
            reasoning_effort="high",
        )
    else:
        base["temperature"] = 0.7

    stream = client.chat.completions.create(**base)
    full = []
    interrupted = False
    for chunk in stream:
        if check_stop and check_stop():
            interrupted = True
            break
        delta = chunk.choices[0].delta
        reasoning = getattr(delta, "reasoning_content", None)
        if thinking and on_thinking and reasoning:
            on_thinking(reasoning)
            continue
        content = delta.content
        if content:
            full.append(content)
            on_token(content)
    return "".join(full), interrupted
