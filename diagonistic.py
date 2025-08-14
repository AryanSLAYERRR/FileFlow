import sys, os
sys.path.append(os.getcwd())

from src.config import load_config, get_default_config_path
from src.scanner import scan_paths

cfg = load_config(get_default_config_path())
include_paths = cfg.get("include_paths", [])
exclude_patterns = cfg.get("exclude_globs", [])
include_hidden = cfg.get("ui", {}).get("show_hidden", False)

print("=== Non-recursive (should show ONLY root-level files) ===")
for p, _ in scan_paths(include_paths, exclude_patterns, include_hidden, include_subfolders=False):
    print("ROOT:", p)

print("\n=== Recursive (should show subfolder files) ===")
for p, _ in scan_paths(include_paths, exclude_patterns, include_hidden, include_subfolders=True):
    if os.path.dirname(p).lower() != include_paths[0].lower():
        print("SUB:", p)
        break
