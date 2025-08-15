import os
from typing import Dict, Generator, Tuple
from .scanner import scan_paths
from .rules import resolve_for_file
from .utils.hash_utils import file_hash

PreviewItem = Tuple[str, str, str]

def _match_base_dir_for(src_path: str, include_paths: list[str]) -> str | None:
    src_abs = os.path.abspath(src_path)
    best = None
    for base in include_paths:
        base_abs = os.path.abspath(base)
        if src_abs.startswith(base_abs.rstrip(os.sep) + os.sep) or src_abs == base_abs:
            if best is None or len(base_abs) > len(os.path.abspath(best)):
                best = base
    return best

import re
_SUFFIX_RE = re.compile(r"^(?P<base>.*) \((?P<num>\d+)\)$")

def _next_suffixed_name(path: str) -> str:
    ddir, fname = os.path.split(path)
    base, ext = os.path.splitext(fname)
    m = _SUFFIX_RE.match(base)
    if m:
        base_core = m.group("base")
        n = int(m.group("num")) + 1
        new_base = f"{base_core} ({n})"
    else:
        new_base = f"{base} (1)"
    return os.path.join(ddir, new_base + ext)

def _suffix_path_chain(dest_path: str, proposed: set) -> str:
    candidate = _next_suffixed_name(dest_path)
    while os.path.exists(candidate) or candidate in proposed:
        candidate = _next_suffixed_name(candidate)
    return candidate

def build_preview(cfg: Dict) -> Generator[PreviewItem, None, None]:
    include_paths = cfg.get("include_paths", [])
    exclude_patterns = cfg.get("exclude_globs", [])
    include_hidden = cfg.get("ui", {}).get("show_hidden_files", False)
    include_subfolders = cfg.get("behavior", {}).get("sort_subfolders", True)
    policy = cfg.get("behavior", {}).get("conflict_policy", "suffix").lower()

    proposed: set[str] = set()

    for src_path, ext in scan_paths(include_paths, exclude_patterns, include_hidden, include_subfolders):
        dest_folder_name = resolve_for_file(ext, cfg)

        current_folder = os.path.basename(os.path.dirname(src_path)).lower()
        if current_folder == dest_folder_name.lower():
            yield src_path, "SKIP", src_path
            continue

        base_root = _match_base_dir_for(src_path, include_paths) or (include_paths[0] if include_paths else "")
        dest_roots = cfg.get("destination_roots", [])
        try:
            idx = include_paths.index(base_root)
        except ValueError:
            idx = 0
        dest_base_dir = (dest_roots[idx] if idx < len(dest_roots) and dest_roots[idx] else base_root)

        dest_path = os.path.join(dest_base_dir, dest_folder_name, os.path.basename(src_path))

        if os.path.abspath(src_path) == os.path.abspath(dest_path):
            yield src_path, "SKIP", dest_path
            continue

        # Conflict handling
        if os.path.exists(dest_path) or dest_path in proposed:
            # if same hash, skip as duplicate
            try:
                if os.path.exists(dest_path):
                    if file_hash(src_path) == file_hash(dest_path):
                        yield src_path, "SKIP", dest_path  # duplicate same content
                        continue
            except Exception:
                # If hashing fails
                pass

            if policy == "suffix":
                final_dest = _suffix_path_chain(dest_path, proposed)
                proposed.add(final_dest)
                yield src_path, "MOVE", final_dest
            else:
                yield src_path, "CONFLICT", dest_path
        else:
            proposed.add(dest_path)
            yield src_path, "MOVE", dest_path
