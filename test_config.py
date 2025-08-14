import sys, os
sys.path.append(os.getcwd())

from src.config import (
get_default_config,
save_config,
load_config,
resolve_destination_for_extension,
get_default_config_path,
)

p = get_default_config_path()
cfg = get_default_config()
save_config(cfg, p)
cfg2 = load_config(p)

print("Type of cfg2:", type(cfg2))
print("Loaded include_paths:", cfg2.get("include_paths"))
print("Dest .mp3 ->", resolve_destination_for_extension(".mp3", cfg2))
print("Dest .unknown ->", resolve_destination_for_extension(".foo", cfg2))