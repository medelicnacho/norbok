# ============================================================
# TEACHING: This script had two main problems that I fixed.
#
# 1. URL typo - double colon "::" after localhost.
#    A valid host:port is "localhost:11434" (single colon).
#    Double colon makes the address an invalid IPv6 reference,
#    so the request always fails.
#
# 2. No error handling - if the request fails (network down,
#    server not running, unexpected reply) the script dies with
#    a hard-to-understand traceback.  I added try/except blocks
#    to catch common problems and print friendly messages.
#
# Additionally, I added a check for the HTTP status code and
# for correct JSON format so that the script doesn’t crash
# when the server sends an error page or an unexpected body.
# ============================================================

import requests

# --- Fixed URL: single colon between host and port ---
url = "http://localhost:11434/api/chat"

payload = {
    "model": "qwen2.5-coder:7b",
    "messages": [{"role": "user", "content": "hello"}],
    "stream": False
}

try:
    response = requests.post(url, json=payload, timeout=10)
except requests.exceptions.RequestException as e:
    # This catches connection errors, timeouts, etc.
    print("❌ Network error:", e)
    exit(1)

# --- Check if the server answered successfully ---
if response.status_code != 200:
    print(f"❌ Server returned HTTP {response.status_code}: {response.text}")
    exit(1)

# --- Try to interpret the body as JSON ---
try:
    data = response.json()
except ValueError:
    print("❌ Response is not valid JSON:", response.text)
    exit(1)

# --- Access the assistant's reply safely ---
try:
    content = data["message"]["content"]
    print(content)
except KeyError as e:
    print("❌ Missing expected key in response:", e)
    print("Raw response:", response.text)
