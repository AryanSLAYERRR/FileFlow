import os
from typing import Dict, Generator, Tuple
from .scanner import scan_paths
from .rules import resolve_for_file

PreviewItem = Tuple[str, str, str]

def build_preview(cfg: Dict) -> Generator[PreviewItem, None, None]:
    include_paths = cfg.get("include_paths", [])
    exclude_patterns = cfg.get("exclude_globs", [])
    include_hidden = cfg.get("ui", {}).get("show_hidden_files", False)
    include_subfolders = cfg.get("behavior", {}).get("sort_subfolders", True)  

    for src_path, ext in scan_paths(include_paths, exclude_patterns, include_hidden, include_subfolders):
        dest_folder_name = resolve_for_file(ext, cfg)
        current_folder = os.path.basename(os.path.dirname(src_path)).lower()
        if current_folder == dest_folder_name.lower():
            yield src_path, "SKIP", src_path
            continue
        dest_base_dir = cfg["include_paths"][0]
        dest_path = os.path.join(dest_base_dir, dest_folder_name, os.path.basename(src_path))

        if os.path.abspath(src_path) == os.path.abspath(dest_path):
            action = "SKIP"
        elif os.path.exists(dest_path):
            action = "CONFLICT"
        else:
            action = "MOVE"

        yield src_path, action, dest_path
