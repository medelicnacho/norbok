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


# Pre‑compute the set of **all** prerequisites (direct + transitive) for each topic.
# Topics are ordered so that every prerequisite appears earlier in TOPICS,
# allowing a simple forward pass.
_ANCESTORS = {}
for topic in TOPICS:
    ancestors = set()
    for prereq_id in topic["prereqs"]:
        ancestors.add(prereq_id)
        ancestors.update(_ANCESTORS.get(prereq_id, set()))
    _ANCESTORS[topic["id"]] = ancestors


def get_topic(topic_id: str) -> dict | None:
    return next((t for t in TOPICS if t["id"] == topic_id), None)


def compute_percent(progress: dict) -> int:
    """
    Given a progress dict {topic_id: 'not_started'|'in_progress'|'complete'},
    return the integer percentage of Python mastered.

    Only 'complete' topics count toward the score.
    The percentage returned is the pct of the highest completed topic
    whose prereqs are **all** also complete — i.e. **transitively** no gaps.

    If nothing is complete, return 0.
    """
    complete = {tid for tid, status in progress.items() if status == "complete"}
    highest = 0
    for topic in TOPICS:
        if topic["id"] in complete:
            if _ANCESTORS[topic["id"]].issubset(complete):
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


if __name__ == "__main__":
    # Verify transitive prerequisite checking (no gaps)
    # functions: ["loops"], loops: ["control_flow"], control_flow: ["variables"]
    # variables has no prerequisites.

    # Only mark functions complete -> 0% (missing loops, control_flow, variables)
    progress = {"functions": "complete", "lists": "complete"}
    pct = compute_percent(progress)
    assert pct == 0, f"Expected 0% for gaps, got {pct}%"

    # Add variables -> 5% (variables counts as highest complete with no missing ancestors)
    progress["variables"] = "complete"
    pct = compute_percent(progress)
    assert pct == 5, f"Expected 5%, got {pct}%"

    # Add control_flow -> 10% (variables already counted, control_flow higher)
    progress["control_flow"] = "complete"
    pct = compute_percent(progress)
    assert pct == 10, f"Expected 10%, got {pct}%"

    # Add loops -> 15%
    progress["loops"] = "complete"
    pct = compute_percent(progress)
    assert pct == 15, f"Expected 15%, got {pct}%"

    print("All curriculum transitive prerequisite tests passed.")
