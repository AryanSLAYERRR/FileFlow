import sys
import os
sys.path.append(os.getcwd())
from src.config import load_config, get_default_config_path
from src.preview import build_preview
from src.apply_moves import apply_moves, undo_last, undo_all_stream

cfg = load_config(get_default_config_path())
undo_q = input("Undo previous sort? (a = all, Enter = skip): ").strip().lower()
if undo_q == "a":
    undo_all_stream(cfg)
    sys.exit(0)
elif undo_q not in {"", "n", "no"}:
    print("Skipping undo.")

subfolder_q = input("Sort inside subfolders as well? (y/N): ").strip().lower()
cfg["behavior"]["sort_subfolders"] = (subfolder_q == "y")

print("\n=== DRY RUN PREVIEW ===")
apply_moves(build_preview(cfg), cfg, dry_run=True)

confirm = input("\nApply the above moves for real? (y/N): ").strip().lower()
if confirm not in {"y", "n"}:
    print("Invalid input, skipping real run.")
    sys.exit(0)
if confirm == "y":
    apply_moves(build_preview(cfg), cfg, dry_run=False) 

    undo_q = input("\nDo you want to UNDO this run right now? (y/N): ").strip().lower()
    if undo_q == "y":
        undo_all_stream(cfg)
else:
    print("No changes applied.")
