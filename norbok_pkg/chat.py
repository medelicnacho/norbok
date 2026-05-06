import os
import ollama

RECOMMENDED_ENV = {
    "OLLAMA_FLASH_ATTENTION": "1",
    "OLLAMA_KV_CACHE_TYPE": "q8_0",
    "OLLAMA_NUM_PARALLEL": "1",
    "OLLAMA_MAX_LOADED_MODELS": "1",
}

def check_ollama_env():
    missing = []
    for key, val in RECOMMENDED_ENV.items():
        if os.environ.get(key) != val:
            missing.append(key)
    if missing:
        print(f"Warning: recommended Ollama server environment variables not set: {', '.join(missing)}")
        print("Set them before starting the Ollama server for best performance.")
    else:
        print("Ollama environment check passed (all recommended vars set).")

def chat(client, messages, model, on_token, check_stop=None):
    stream = client.chat(
        model=model,
        messages=messages,
        stream=True,
        keep_alive="30m",
        options={
            "num_ctx": 8192,
            "num_predict": 1024,
            "num_thread": max(1, (os.cpu_count() or 4) // 2),
            "num_batch": 256,
            "low_vram": False,
            "temperature": 0.7,
            "repeat_penalty": 1.1,
        },
    )
    full = []
    for chunk in stream:
        if check_stop and check_stop():
            break
        token = chunk["message"]["content"]
        full.append(token)
        on_token(token)
    return "".join(full)
