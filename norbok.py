# We need the requests library so we can talk to the Ollama API over HTTP
import requests

# The chat function takes the full conversation history (a list of message
# dictionaries) and returns the model's next reply.
def chat(messages):
    # Fixed model name: "qwne2.5-coder:0.5b" was a typo, correct name is "qwen2.5-coder:0.5b"
    # Send a POST request to Ollama's local server. The /api/chat endpoint
    # expects a JSON body containing the model name, the messages, and an
    # option to turn streaming off.
    response = requests.post(
        "http://localhost:11434/api/chat",   # default address where Ollama listens
        json={
            "model": "qwen2.5-coder:0.5b",  # exact model name we want to use
            "messages": messages,            # conversation up to this point
            "stream": False                  # ask for the whole answer at once
        }
    )
    # Return the assistant's answer from the response dictionary.
    # response.json() turns the server's JSON reply into a Python dict.
    # ["message"]["content"] drills down to the actual text the model returned.
    return response.json()["message"]["content"]

# Create an empty list that will store the entire conversation (every user
# message and every assistant reply).
messages = []

# Fixed typo: changed "quick" to "quit" and added a period + space for readability
# Show a friendly startup message that tells the user how to exit the program.
print("Norbok is ready to teach. Type 'exit' to quit.\n")

# Start an infinite loop so we can keep accepting messages until the user
# decides to stop.
while True:
    # Wait for the user to type something and press Enter. The prompt "student: "
    # appears before the cursor so they know where to type.
    user_input = input("student: ")

    # Check whether the user wants to leave.
    # .strip() removes any leading/trailing spaces.
    # .lower() makes it lowercase so that "EXIT", "Exit", etc. are all recognized.
    if user_input.strip().lower() == "exit":
        # Say goodbye and break out of the while loop, ending the program.
        print("peace bro")
        break

    # Append the user's input exactly as typed (keeps leading/trailing spaces).
    # We store it as a dictionary where "role" is "user" and "content" is what
    # they typed.
    messages.append({"role": "user", "content": user_input})

    # Send the whole conversation (including the new user message) to the LLM
    # and get back a string containing the assistant's reply.
    reply = chat(messages)

    # Add the assistant's reply to the conversation history so the model
    # remembers what it said for the next turn.
    messages.append({"role": "assistant", "content": reply})

    # Print a blank line for spacing, then the assistant's reply with the
    # prefix "Norbok: ", followed by another blank line to keep the chat
    # readable.
    print(f"\nNorbok: {reply}\n")
