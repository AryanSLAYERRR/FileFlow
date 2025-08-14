import sys, os
sys.path.append(os.getcwd())
from src.config import get_default_config, get_default_config_path, load_config, save_config
from src.preview import build_preview

cfg_path = get_default_config_path()
if not os.path.exists(cfg_path):
    save_config(get_default_config(), cfg_path)
cfg = load_config(cfg_path)
print("Scanning:", cfg["include_paths"])
for i, (src, action, dest) in enumerate(build_preview(cfg), start=1):
    print(f"{i:04d} | {action:<8} | {src} -> {dest}")

    if i >= 20:
        break
