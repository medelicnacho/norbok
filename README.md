# norbok >:3
### project‑first Socratic code mentor — built for the world, not for a wallet

A terminal‑based AI tutor that teaches by asking questions, tracks what you
struggle with (spaced repetition), quizzes you when you need it, and never
just hands you an answer.  Everything connects to *your* real project.

Built entirely on DeepSeek.  No accounts, no cloud, no telemetry.
Runs on your machine.  Roughly **$5/month** in API costs.

---

## what makes norbok different

**Socratic by design** — before explaining anything, Norbok asks what you've
tried.  The socratic guard is baked into every response; it cannot be
overridden by the student.  You learn by producing, not by reading.

**Memory that sticks** — every concept you or the AI identifies as shaky
goes into a spaced‑repetition system.  Norbok quizzes you at the right
intervals.  Concepts you nail graduate off the list; concepts you keep
missing come back sooner.

**Checkpoints, not lectures** — after 2–3 confirmed concepts, Norbok issues
a **CHECKPOINT**: a small function challenge (under 15 lines) that you write
with `/code`.  After submission, it reviews your work part by part and asks
*what would break if you removed one specific line?* – real understanding,
not parroting.

**Project‑first mentoring** — the very first message asks what you want to
build and what you already know.  Everything Norbok teaches stays anchored
to your actual project.  Roadmaps have numbered steps; progress is announced
step by step.

**Curriculum with depth** — a 20‑topic Python curriculum (variables →
async/await → advanced patterns) tracks your real progress (0–100%).
Topics unlock only when all prerequisites are solid.

**OS‑aware** — terminal commands are given for macOS, Linux, or Windows.
Norbok auto‑detects your OS or you can set it with `/setos`.

**Local & private** — your conversations, SRS data, and curriculum progress
live in JSON files on your machine.  Delete them and you start fresh.

---

## requirements

- Python 3.10+
- A DeepSeek API key – free at <https://platform.deepseek.com/api_keys>
  (new accounts get 5 million free tokens, no credit card needed)

---

## install

```bash
pip install norbok

Or clone and install locally:

git clone https://github.com/medelicnacho/norbok.git
cd norbok
pip install -e .

run
norbok

The first run asks for your DeepSeek API key and saves it to a local
.env file inside ~/.config/norbok/ (Linux/macOS) or
%APPDATA%/norbok/ (Windows). You never have to re‑enter it.

save slots & session resumption

Norbok keeps 5 save slots. Each slot stores:

    what you’re building and your coding level (beginner/intermediate/advanced)

    a summary of the last session

    all shaky concepts with spaced‑repetition scheduling

    your Python curriculum progress

    your known operating system

When you load a slot, Norbok checks which concepts are due for review and
gently quizzes you before the session starts. It remembers who you are,
where you left off, and what still needs work.
commands
command	what it does
/quiz	quiz on a shaky concept due today (random choice)
/quiz <concept>	quiz on a specific concept
/curriculum	show full Python progress (0–100%) and suggested topics
/curriculum <topic>	mark a topic as in progress
/progress	spaced‑repetition status — what’s due, what’s learned
/think	enable deep reasoning mode (slower, smarter)
/nothink	disable reasoning mode
/switch	change model mid‑session
/code	open multiline Python editor (Ctrl+D to submit)
/setos linux/macos/windows/auto	set or auto‑detect your operating system
/save	save current session to current slot
/saveas	pick a different slot to save into (with overwrite guard)
/delete_session	wipe current conversation and assigned slot
/exit	save (if a slot is assigned) and quit
models
model	note
deepseek-v4-pro	smartest, slower — reasoning mode available
deepseek-v4-flash	fast and cheap — great for day‑to‑day

The model names above are the identifiers used in the code; they may map
to specific DeepSeek model IDs depending on your installation.
how the spaced repetition works

Every concept in your shaky list has an interval that adjusts after a quiz:

    nailed it → interval doubles (review in 2 days → 4 → 8 …)

    partial → interval grows slightly slower

    missed it → interval resets to 1 day

Once a concept has been recalled correctly over a 30‑day window, it
graduates off the shaky list entirely. Use /progress to see where
everything stands.
how the curriculum progress works

The Python curriculum has 20 topics in dependency order. Topics are marked
complete, in_progress, or not_started. Your overall percentage is the
pct of the highest topic whose all transitive prerequisites are also
complete. No cheating — you can’t jump ahead with gaps.
checkpoint system (automatic)

When Norbok sees you’ve understood 2–3 concepts, it will start a message
with CHECKPOINT: and give you a small coding challenge (under 15 lines).

    Write your solution with /code (or paste a code block).

    Norbok will then review it line by line, then ask a “what breaks if…”
    question that you must answer before moving on.

    No new checkpoint is issued until the previous one is fully resolved.
    
    data

Everything is stored in your platform‑specific config directory:
text

Linux/macOS:   ~/.config/norbok/
Windows:       %APPDATA%\norbok\

Inside that folder you will find:

    slot_1.json … slot_5.json – session save slots

    .env – your DeepSeek API key

Delete any slot file to free it; delete .env to go through onboarding again.
vision & roadmap

    Local offline version: distill Norbok into a small model that runs on
    an old laptop or a Raspberry Pi, no internet required.

    Multilingual: Spanish first, then gradually more languages, so that
    code can be taught in the student’s mother tongue.

    Always free, always private: no monetisation, no analytics, no lock‑in.
    A gift for anyone who wants to learn Python, wherever they are.

why not just use ChatGPT

ChatGPT doesn’t remember what you’re building, what you struggle with, or how
long it’s been since you last practiced a concept. It won’t refuse to give
you the answer when you should figure it out yourself. Norbok does all of
that – it’s a mentor, not an autocomplete – and it costs less than a cup of
coffee a month.

    May Norbok benefit all sentient beings in the ten directions. >:3





