import json
import os
from datetime import date

SAVES_DIR = "saves"
NUM_SLOTS = 5


def _ensure_dir():
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)


def load_slot(n):
    """
    Load save data for slot n (1‑5).

    Returns a dict with keys:
        slot_number, project_name, coding_level, summary, shaky_concepts,
        learned_concepts, curriculum_progress
    or None if the slot does not exist or contains corrupt data.
    """
    if n < 1 or n > NUM_SLOTS:
        raise ValueError(f"Slot number must be between 1 and {NUM_SLOTS} (inclusive)")

    filepath = os.path.join(SAVES_DIR, f"slot_{n}.json")
    if not os.path.isfile(filepath):
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        # Migrate older saves that lack curriculum_progress
        if "curriculum_progress" not in data:
            data["curriculum_progress"] = {}

        # Migrate missing learned_concepts
        if "learned_concepts" not in data:
            data["learned_concepts"] = {}

        # Migrate shaky_concepts from old list format to SRS dict format
        if isinstance(data.get("shaky_concepts"), list):
            today_iso = date.today().isoformat()
            old_list = data["shaky_concepts"]
            data["shaky_concepts"] = {
                concept: {
                    "added": today_iso,
                    "interval_days": 1,
                    "next_review": today_iso,
                    "history": []
                }
                for concept in old_list
                if isinstance(concept, str)
            }

        return data
    except (json.JSONDecodeError, OSError):
        return None


def write_slot(n, data):
    """
    Write save data to slot n (1‑5).

    *data* must be a dict containing at least some of the keys
    project_name, coding_level, summary, shaky_concepts, learned_concepts,
    curriculum_progress.
    The slot_number field is automatically set to n.
    """
    if n < 1 or n > NUM_SLOTS:
        raise ValueError(f"Slot number must be between 1 and {NUM_SLOTS} (inclusive)")

    _ensure_dir()

    allowed_keys = {
        "project_name",
        "coding_level",
        "summary",
        "shaky_concepts",
        "learned_concepts",
        "curriculum_progress",
    }
    record = {"slot_number": n}
    for key in allowed_keys:
        # Default to {} for the dict-type keys, None for text keys
        if key in ("learned_concepts", "curriculum_progress"):
            record[key] = data.get(key, {})
        else:
            record[key] = data.get(key, None)

    # Ensure dict-type fields are actually dicts
    if not isinstance(record.get("learned_concepts"), dict):
        record["learned_concepts"] = {}
    if not isinstance(record.get("curriculum_progress"), dict):
        record["curriculum_progress"] = {}

    filepath = os.path.join(SAVES_DIR, f"slot_{n}.json")
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2)


def list_slots():
    """
    Return the state of all 5 save slots.

    Each entry is a dict with:
        slot    – int (1‑5)
        status  – "filled" or "empty"
        data    – the full save dict if the slot is filled, else None
    """
    result = []
    for n in range(1, NUM_SLOTS + 1):
        data = load_slot(n)
        if data is not None:
            result.append({"slot": n, "status": "filled", "data": data})
        else:
            result.append({"slot": n, "status": "empty", "data": None})
    return result


def delete_slot(n):
    """
    Delete the save file for slot n (1‑5).

    Returns True if the file existed and was removed, False otherwise.
    """
    if n < 1 or n > NUM_SLOTS:
        raise ValueError(f"Slot number must be between 1 and {NUM_SLOTS} (inclusive)")

    filepath = os.path.join(SAVES_DIR, f"slot_{n}.json")
    if os.path.isfile(filepath):
        os.remove(filepath)
        return True
    return False
