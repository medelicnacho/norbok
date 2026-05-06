import requests

def chat(messages):
    # Fixed model name: "qwne2.5-coder:0.5b" was a typo, correct name is "qwen2.5-coder:0.5b"
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwen2.5-coder:0.5b",
            "messages": messages,
            "stream": False
        }
    )
    # Return the assistant's answer from the response dictionary
    return response.json()["message"]["content"]

messages = []

# Fixed typo: changed "quick" to "quit" and added a period + space for readability
print("Norbok is ready to teach. Type 'exit' to quit.\n")

while True:
    user_input = input("student: ")

    if user_input.strip().lower() == "exit":
        print("peace bro")
        break
    # Append the user's input exactly as typed (keeps leading/trailing spaces)
    messages.append({"role": "user", "content": user_input}) 
    reply = chat(messages)
    messages.append({"role": "assistant", "content": reply})

    print(f"\nNorbok: {reply}\n")
