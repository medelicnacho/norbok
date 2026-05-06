import requests

def chat(message):
	response = requests.post(
	"http://localhost:11434/api/chat",
		json={
			"model": "qwen2.5-coder:0.5b",
			"messages": messages,
			"stream": False

		}
	)
	return response.json()["message"]["content"]

def run():
	messages = []
	print("Norbok is ready to teach >:3 - Type 'exit' to quit.\n")

	while True:
		user-input = input("student: ")

		if user._input.strip().lower() == "exit":
			print("peace bro >:3")
			break

		messages.append({"role": "user", "content": user_input})
		reply = chat(messages)
		messages.append({"role": "assistant", "content": reply})
		print(f"\nNorbok: {reply}\n")