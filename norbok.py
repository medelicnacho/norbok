"""
Norbok - A simple AI tutor that chats with you via the Ollama API.

This script does the following:
1. It sends each of your questions to a local AI model (qwen2.5-coder:0.5b)
   running on your computer through the Ollama service.
2. The model remembers the whole conversation because we keep a list of
   messages (both user and assistant) and send the full list every time.
3. When you type a message, it is added to the list, then the list is sent
   to the model. The model's reply is also added to the list.
4. The program loops forever until you type 'exit', then it says goodbye
   and stops.

Key pieces:
- requests.post(...) talks to the Ollama server at localhost:11434.
- The /api/chat endpoint expects a JSON object with:
    - "model": the name of the model to use,
    - "messages": A list of message dictionaries, each with "role" and "content".
    - "stream": False tells the server to return the full answer at once.
- The response contains a "message" key, whose value has a "content" key
  that holds the assistant's answer as a string.
- The messages variable is a Python list that starts empty and grows as the
  conversation goes on.
- input("student: ") waits for the user to type something and press Enter.
- The if user_input.strip().lower() == "exit": check lets the user quit by
  typing "exit" (even with extra spaces or different case).
- We use print(f"\nNorbok: {reply}\n") to display each reply nicely on a
  new line.
"""

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
