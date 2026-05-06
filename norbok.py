import requests

def chat(messages):

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwne2.5-coder:0.5b",
            "messages": messages,
            "stream": False
        }
    )
    return response.json()["message"]["content"]

messages = []

print("Norbok is ready to teach type 'exit' to quick.\n")

while True:
    user_input = input("student: ")

    if user_input.strip().lower() == "exit":
        print("peace bro")
        break
    messages.append({"role": "user", "content": user_input}) 
    reply = chat(messages)
    messages.append({"role": "assistant", "content": reply})

    print(f"\nNorbok: {reply}\n")