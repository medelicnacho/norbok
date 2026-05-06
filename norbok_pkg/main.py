from .chat import chat
from .ui import print_welcome, print_reply, get_input

def run():
    messages = [
        {"role": "system", "content": "You are Norbok, a snarky but helpful coding tutor. >:3"}
    ]
    print_welcome()
    while True:
        try:
            user_input = get_input()
        except (EOFError, KeyboardInterrupt):
            print("\nPeace brasskee >:3")
            break
        if user_input.strip().lower() == "exit":
            print("peace bro >:3")
            break
        messages.append({"role": "user", "content": user_input})
        reply = chat(messages)
        messages.append({"role": "assistant", "content": reply})
        print_reply(reply)