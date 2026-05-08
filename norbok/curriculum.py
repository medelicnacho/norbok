TOPICS = [
    {"id": "variables",        "title": "Variables & Types",        "pct": 5,  "prereqs": []},
    {"id": "control_flow",     "title": "If / Else",                "pct": 10, "prereqs": ["variables"]},
    {"id": "loops",            "title": "For & While Loops",        "pct": 15, "prereqs": ["control_flow"]},
    {"id": "functions",        "title": "Functions",                "pct": 22, "prereqs": ["loops"]},
    {"id": "lists",            "title": "Lists & Indexing",         "pct": 28, "prereqs": ["functions"]},
    {"id": "dicts",            "title": "Dicts & Sets",             "pct": 34, "prereqs": ["lists"]},
    {"id": "strings",          "title": "String Methods",           "pct": 38, "prereqs": ["dicts"]},
    {"id": "file_io",          "title": "File I/O",                 "pct": 43, "prereqs": ["strings"]},
    {"id": "errors",           "title": "Error Handling",           "pct": 48, "prereqs": ["file_io"]},
    {"id": "comprehensions",   "title": "List Comprehensions",      "pct": 53, "prereqs": ["errors"]},
    {"id": "oop",              "title": "Classes & OOP",            "pct": 62, "prereqs": ["comprehensions"]},
    {"id": "modules",          "title": "Modules & Imports",        "pct": 66, "prereqs": ["oop"]},
    {"id": "iterators",        "title": "Iterators & Generators",   "pct": 71, "prereqs": ["modules"]},
    {"id": "decorators",       "title": "Decorators",               "pct": 76, "prereqs": ["iterators"]},
    {"id": "context_managers", "title": "Context Managers",         "pct": 80, "prereqs": ["decorators"]},
    {"id": "async",            "title": "Async / Await",            "pct": 86, "prereqs": ["context_managers"]},
    {"id": "type_hints",       "title": "Type Hints",               "pct": 89, "prereqs": ["async"]},
    {"id": "testing",          "title": "Testing (pytest)",         "pct": 93, "prereqs": ["type_hints"]},
    {"id": "packaging",        "title": "Packaging & pip",          "pct": 96, "prereqs": ["testing"]},
    {"id": "patterns",         "title": "Advanced Patterns",        "pct": 100,"prereqs": ["packaging"]},
]

def get_topic(topic_id: str) -> dict | None:
    return next((t for t in TOPICS if t["id"] == topic_id), None)

def compute_percent(progress: dict) -> int:
    """
    Given a progress dict {topic_id: 'not_started'|'in_progress'|'complete'},
    return the integer percentage of Python mastered.
    
    Only 'complete' topics count toward the score.
    The percentage returned is the pct of the highest completed topic
    whose prereqs are all also complete — i.e. no gaps.
    
    If nothing is complete, return 0.
    """
    complete = {tid for tid, status in progress.items() if status == "complete"}
    
    highest = 0
    for topic in TOPICS:
        if topic["id"] in complete:
            all_prereqs_done = all(p in complete for p in topic["prereqs"])
            if all_prereqs_done:
                highest = max(highest, topic["pct"])
    return highest

def next_topics(progress: dict, n: int = 3) -> list[dict]:
    """
    Return up to n topics the student should work on next:
    topics whose prereqs are all complete but are not yet complete 
    themselves, sorted by pct ascending.
    """
    complete = {tid for tid, status in progress.items() if status == "complete"}
    candidates = []
    for topic in TOPICS:
        if topic["id"] in complete:
            continue
        if all(p in complete for p in topic["prereqs"]):
            candidates.append(topic)
    return candidates[:n]
