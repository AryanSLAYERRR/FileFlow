from src.config import load_config, get_default_config_path
from src.scanner import scan_paths
cfg = load_config(get_default_config_path())

for p, _ in scan_paths(cfg["include_paths"], cfg.get("exclude_globs", []), False):
    print(p)
