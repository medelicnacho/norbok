import json
import os
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

def _get_data_dir():
    if os.name == 'nt':
        base = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    else:
        xdg = os.environ.get('XDG_CONFIG_HOME')
        if xdg:
            base = Path(xdg)
        else:
            base = Path.home() / '.config'
    return base / 'norbok'

SAVES_DIR = str(_get_data_dir())

NUM_SLOTS = 5

_OLD_SAVES_NOTIFIED = False


def _ensure_dir():
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR, exist_ok=True)
    global _OLD_SAVES_NOTIFIED
    if not _OLD_SAVES_NOTIFIED:
        _OLD_SAVES_NOTIFIED = True
        if os.path.isdir("./saves"):
            print(
                "Old './saves' directory found. "
                "Move its contents to %s (or %APPDATA%/norbok on Windows) and delete it."
                % SAVES_DIR
            )


def _migrate_slot(n, data):
    """Apply slot-level migrations and persist the result.

    Returns the migrated data dict.
    Any write failure is logged to stderr but does not prevent the
    returned data from being used.
    """
    # Work on a copy to be safe.
    migrated = dict(data)

    # Ensure curriculum_progress exists.
    if "curriculum_progress" not in migrated:
        migrated["curriculum_progress"] = {}

    # Ensure learned_concepts exists.
    if "learned_concepts" not in migrated:
        migrated["learned_concepts"] = {}

    # Migrate old list-based shaky_concepts to the SRS dict format.
    if isinstance(migrated.get("shaky_concepts"), list):
        today_iso = date.today().isoformat()
        old_list = migrated["shaky_concepts"]
        migrated["shaky_concepts"] = {
            concept: {
                "added": today_iso,
                "interval_days": 1,
                "next_review": today_iso,
                "history": []
            }
            for concept in old_list
            if isinstance(concept, str)
        }

    try:
        write_slot(n, migrated)
    except Exception as e:
        print(f"Warning: failed to write migrated slot {n}: {e}", file=sys.stderr)

    return migrated


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

        # Apply any slot-level migrations (and persist them).
        data = _migrate_slot(n, data)

        return data
    except json.JSONDecodeError:
        # rename the corrupt file to a backup
        new_path = os.path.join(SAVES_DIR, f"slot_{n}.corrupt.{int(time.time())}.bak")
        try:
            os.replace(filepath, new_path)
        except Exception:
            pass
        print(
            f"Warning: slot {n} JSON is corrupt; moved to {new_path}",
            file=sys.stderr,
        )
        return None
    except OSError:
        return None


def write_slot(n, data):
    """
    Write save data to slot n (1‑5) atomically to avoid corruption.

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
        "known_os",
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

    # Atomic write via a temporary file in the same directory
    fd, tmp_path = tempfile.mkstemp(suffix=".tmp", prefix="slot_", dir=SAVES_DIR)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmpf:
            json.dump(record, tmpf, indent=2)
        os.replace(tmp_path, filepath)
    except Exception:
        # Clean up the temporary file on failure
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


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
    try:
        os.remove(filepath)
        return True
    except FileNotFoundError:
        return False
