import os
import fnmatch
from typing import Generator, List, Tuple

def _should_exclude(path: str, exclude_patterns: List[str]) -> bool:
    base = os.path.basename(path)
    for pat in exclude_patterns:
        if fnmatch.fnmatch(base, pat):
            return True
    return False

def _dir_should_exclude(dir_name: str, exclude_patterns: List[str]) -> bool:
    for pat in exclude_patterns:
        if fnmatch.fnmatch(dir_name, pat):
            return True
    return False

def scan_paths(paths: list[str],
               exclude_patterns: list[str],
               include_hidden: bool = False,
               include_subfolders: bool = True) -> Generator[tuple[str, str], None, None]:

    for root_path in paths:
        if not os.path.exists(root_path):
            continue

        if include_subfolders:
            for dirpath, dirnames, filenames in os.walk(root_path):
                if not include_hidden:
                    dirnames[:] = [d for d in dirnames if not d.startswith(".")]
                dirnames[:] = [d for d in dirnames if not _dir_should_exclude(d, exclude_patterns)]
                for fname in filenames:
                    # Skip hidden files if requested
                    if not include_hidden and fname.startswith("."):
                        continue
                    full_path = os.path.join(dirpath, fname)
                    # Skip excluded files
                    if _should_exclude(full_path, exclude_patterns):
                        continue
                    _, ext = os.path.splitext(fname)
                    yield full_path, ext
        else:
            try:
                for fname in os.listdir(root_path):
                    full_path = os.path.join(root_path, fname)
                    if not os.path.isfile(full_path):
                        continue
                    if not include_hidden and fname.startswith("."):
                        continue
                    if _should_exclude(full_path, exclude_patterns):
                        continue
                    _, ext = os.path.splitext(fname)
                    yield full_path, ext
            except OSError:
                continue
