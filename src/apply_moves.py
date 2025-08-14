import os
import shutil
from typing import Dict, Iterable, Tuple
import json
import time

PreviewItem = Tuple[str, str, str]

def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _journal_path(cfg: Dict) -> str:
    return os.path.join(cfg["include_paths"][0], ".fileflow_journal.jsonl")

def _append_journal(cfg: Dict, src_before: str, dest_after: str) -> None:
    path = _journal_path(cfg)
    entry = {
        "src_before": src_before,
        "dest_after": dest_after,
        "time": _now_iso()
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _resolve_conflict(dest: str, policy: str) -> str:
    if not os.path.exists(dest):
        return dest
    if policy == "skip":
        return dest
    
    ddir, fname = os.path.split(dest)
    base, ext = os.path.splitext(fname)
    n = 1
    while True:
        candidate = os.path.join(ddir, f"{base} ({n}){ext}")
        if not os.path.exists(candidate):
            return candidate
        n += 1

def apply_moves(preview_stream: Iterable[PreviewItem], cfg: Dict, dry_run: bool = False) -> None:
    policy = cfg.get("behavior", {}).get("conflict_policy", "suffix").lower()
    for src, action, dest in preview_stream:
        if action != "MOVE":
            continue
        final_dest = _resolve_conflict(dest, policy)
        if dry_run:
            print(f"[DRY RUN] Moving {src} --> {final_dest}")
            continue
        try:
            os.makedirs(os.path.dirname(final_dest), exist_ok=True)
            shutil.move(src, final_dest)
            _append_journal(cfg, src, final_dest)
            print(f"[MOVED] {src} --> {final_dest}")
        except Exception as e:
            print(f"[ERROR] Could not move {src} to {final_dest}: {e}")

def undo_last(cfg: Dict) -> None:
    journal_file = _journal_path(cfg)
    if not os.path.exists(journal_file):
        print("No journal found — nothing to undo.")
        return
    with open(journal_file, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    if not lines:
        print("Journal is empty — nothing to undo.")
        return
    latest_time = max(entry["time"] for entry in lines if "time" in entry)
    latest_entries = [e for e in lines if e.get("time") == latest_time]
    count = 0
    for entry in reversed(latest_entries):
        src_before = entry["src_before"]
        dest_after = entry["dest_after"]
        if os.path.exists(dest_after):
            os.makedirs(os.path.dirname(src_before), exist_ok=True)
            shutil.move(dest_after, src_before)
            print(f"[UNDONE] {dest_after} -> {src_before}")
            count += 1

    print(f"Undo complete: {count} files restored.")

def undo_all_stream(cfg: Dict) -> None:
    """
    Memory‑friendly: stream through the journal and undo every recorded move,
    regardless of batch/time, without loading all lines into RAM.
    """
    journal_file = _journal_path(cfg)
    if not os.path.isfile(journal_file):
        print(f"No journal file found at {journal_file}")
        return

    restored = 0
    missing = 0

    print(f"Restoring from journal: {journal_file}\n")
    with open(journal_file, "r", encoding="utf-8") as f:
        lines = list(f)  
    for raw in reversed(lines):
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue

        src_before = entry.get("src_before")
        dest_after = entry.get("dest_after")
        if not src_before or not dest_after:
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
            print(f"[MISSING] {dest_after}")
            missing += 1

    print(f"\n=== Undo Complete ===\nRestored: {restored}\nMissing: {missing}")


