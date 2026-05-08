from datetime import date, timedelta
import copy

GRADUATION_INTERVAL = 30   # days until a concept is considered learned
MAX_INTERVAL = 60          # cap on interval growth


def make_entry(today=None):
    """Return a new concept entry dict."""
    today_iso = today if today else date.today().isoformat()
    return {
        "added": today_iso,
        "interval_days": 1,
        "next_review": today_iso,
        "history": [],
    }


def add_concept(shaky, concept_id, today=None):
    """Add concept_id to shaky if not present; return non‑mutated updated dict."""
    new_shaky = copy.deepcopy(shaky)
    if concept_id not in new_shaky:
        new_shaky[concept_id] = make_entry(today)
    return new_shaky


VALID_RESULTS = {"correct", "partial", "wrong", "gave_up", "skipped"}


def record_result(shaky, concept_id, result, today=None):
    """
    Record a quiz result and update spacing.

    Returns a deep copy; original is never modified.
    """
    # Ignore invalid / None results – do not touch history at all.
    if result not in VALID_RESULTS:
        return copy.deepcopy(shaky)

    today_iso = today if today else date.today().isoformat()
    shaky_copy = copy.deepcopy(shaky)

    entry = shaky_copy.get(concept_id)
    if entry is None:
        return shaky_copy   # nothing to update

    # Always log the result
    entry["history"].append({"date": today_iso, "result": result})

    if result == "skipped":
        return shaky_copy

    # Compute new interval
    old_interval = entry["interval_days"]
    if result == "correct":
        new_interval = min(old_interval * 2, MAX_INTERVAL)
    elif result == "partial":
        new_interval = min(int(old_interval * 1.2) + 1, MAX_INTERVAL)
    elif result in ("wrong", "gave_up"):
        new_interval = 1

    entry["interval_days"] = new_interval
    today_date = date.today() if today is None else date.fromisoformat(today_iso)
    entry["next_review"] = (today_date + timedelta(days=new_interval)).isoformat()
    return shaky_copy


def due_concepts(shaky, today=None):
    """Return list of concept_ids with next_review <= today, most overdue first."""
    today_iso = today if today else date.today().isoformat()
    due = [
        cid for cid, entry in shaky.items()
        if entry.get("next_review", today_iso) <= today_iso
    ]
    due.sort(key=lambda cid: shaky[cid]["next_review"])
    return due


def graduate_concepts(shaky, learned, today=None):
    """
    Promote concepts whose interval_days >= GRADUATION_INTERVAL to learned.

    Returns:
        (new_shaky, new_learned, newly_graduated_ids)
    """
    today_iso = today if today else date.today().isoformat()
    new_shaky = {}
    newly_graduated = []
    new_learned = copy.deepcopy(learned)

    for cid, entry in shaky.items():
        if is_graduated(entry):
            grad_entry = copy.deepcopy(entry)
            grad_entry["graduated"] = today_iso
            new_learned[cid] = grad_entry
            newly_graduated.append(cid)
        else:
            new_shaky[cid] = copy.deepcopy(entry)

    return new_shaky, new_learned, newly_graduated


def is_graduated(entry):
    """Return True if the entry has reached or passed the graduation interval."""
    return entry.get("interval_days", 0) >= GRADUATION_INTERVAL
