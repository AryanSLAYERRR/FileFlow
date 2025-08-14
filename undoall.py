import os
import json
import shutil

DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
JOURNAL_FILE = os.path.join(DOWNLOADS_DIR, ".fileflow_journal.jsonl")


def undo_all():
    if not os.path.isfile(JOURNAL_FILE):
        print(f"No journal file found at {JOURNAL_FILE}")
        return
    restored = 0
    missing = 0

    with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            print(f"[BAD ENTRY] {line}")
            continue

        src_before = entry.get("src_before")
        dest_after = entry.get("dest_after")

        if not src_before or not dest_after:
            print(f"[SKIP] Invalid entry: {entry}")
            continue

        if os.path.exists(dest_after):
            try:
                os.makedirs(os.path.dirname(src_before), exist_ok=True)
                shutil.move(dest_after, src_before)
                print(f"[UNDONE] {dest_after} -> {src_before}")
                restored += 1
            except Exception as e:
                print(f"[ERROR] Could not undo {dest_after}: {e}")
        else:
            print(f"[MISSING] {dest_after} (cannot restore)")
            missing += 1

    print(f"\n=== Undo Complete ===\nRestored: {restored}\nMissing: {missing}")


if __name__ == "__main__":
    undo_all()
