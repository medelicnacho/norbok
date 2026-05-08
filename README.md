# norbok >:3
### project focused Socratic code tutor

A local AI tutor that tracks what you struggle with, quizzes you at the right moment,
and teaches by asking questions — not handing you answers.

Built around your project. Runs on your machine. ~$5/month in API costs.

---

## what makes it different

**Socratic by default** — Norbok asks what you've tried before explaining.
You learn by producing, not consuming.

**Tracks what trips you up** — every concept you struggle with goes into a shaky list.
Norbok quizzes you at the right intervals using spaced repetition so you actually remember it.
Concepts you consistently nail graduate off the list. Ones you keep missing come back sooner.

**Project-first** — before anything else it asks what you want to build and what you already know.
Everything it teaches connects to your actual project, not abstract exercises.

**Local and private** — no account, no cloud, no data leaving your machine.
Your conversations and progress live in JSON files on your computer.

**Python curriculum built in** — track your progress from 0–100% as you demonstrate mastery.
Topics unlock as prerequisites are met.

---

## requirements

- Python 3.10+
- A DeepSeek API key — free at https://platform.deepseek.com/api_keys
  (new accounts get 5 million free tokens, no credit card needed)

---

## install

```bash
pip install norbok
```

or clone and install locally:

```bash
git clone https://github.com/medelicnacho/norbok.git
cd norbok
pip install -e .
```

---

## run

```bash
norbok
```

First run asks for your DeepSeek API key and saves it to a local `.env` file.
You won't need to do it again.

---

## commands

| command | what it does |
|---|---|
| `/quiz` | quiz yourself on a concept due for review today |
| `/quiz <concept>` | quiz on a specific concept |
| `/curriculum` | view Python progress (0–100%) and suggested next topics |
| `/curriculum <topic>` | mark a topic as in progress |
| `/progress` | see your spaced repetition schedule — what's due, what's learned |
| `/think` | enable deep reasoning mode (slower, smarter) |
| `/nothink` | disable reasoning mode |
| `/code` | open multiline code editor with syntax highlighting |
| `/switch` | switch model mid-session |
| `/delete_session` | wipe current session memory and slot |
| `/exit` | save and quit |

---

## models

| model | note |
|---|---|
| `deepseek-v4-pro` | smartest, slower — reasoning mode available |
| `deepseek-v4-flash` | fast and cheap — good for most sessions |

---

## how the memory works

Norbok saves up to 5 session slots. Each slot stores:

- what you're building and your current coding level
- a summary of what was covered last session
- your shaky concepts with spaced repetition scheduling
- your Python curriculum progress

When you load a slot, Norbok checks which concepts are due for review and quizzes
you before the session starts. The quiz formats adapt to the concept — you might be
asked to predict output, write a function from scratch, find a bug, or explain something
back in your own words.

---

## the spaced repetition system

Concepts in your shaky list each have a review interval that adjusts based on quiz results:

- nail it → interval doubles (review in 2 days, then 4, then 8...)
- partial → interval grows slowly
- miss it → resets to 1 day

After consistent correct recall over 30+ days a concept graduates off the shaky list entirely.
Use `/progress` to see where everything stands.

---

## data

Everything lives locally in your project folder:

```
saves/        ← session slots (JSON)
.env          ← your API key
```

Delete either to start fresh. Nothing is stored anywhere else.

---

## why not just use ChatGPT

ChatGPT doesn't know what you're building. It doesn't remember what trips you up.
It doesn't quiz you at the right moment, track whether you're actually getting better,
or push back when you ask for an answer you should figure out yourself.

Norbok does all of that. And it costs about $5/month.
