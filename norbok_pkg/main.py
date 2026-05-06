import requests

def chat(messages):
	response = requests.post(
		"http://localhost:11434/api/chat",
		json={
			"model": "qwen2.5-coder:7b",
			"messages": messages,
			"stream": False
		}
	)
	return response.json()["message"]["content"]

def run():
	messages = [{"role": "system", "content": "You are Norbok, a snarky but helpful coding tutor. >:3"}]
	print("Norbok is ready to teach >:3 - Type 'exit' to quit.\n")

	while True:
		try:
			user_input = input("student: ")
		except (EOFError, KeyboardInterrupt):
			print("\nPeace brasskee >:3")
			break

		if user_input.strip().lower() == "exit":
			print("peace bro >:3")
			break

		messages.append({"role": "user", "content": user_input})
		reply = chat(messages)
		messages.append({"role": "assistant", "content": reply})
		print(f"\nNorbok: {reply}\n")
