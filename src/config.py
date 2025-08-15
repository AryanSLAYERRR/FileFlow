import json
import os
import platform
from typing import Any, Dict, List, Tuple
from .types_map import infer_category, CATEGORY_DESTINATION_DEFAULT

def _user_home( ) -> str:
    return os.path.expanduser("~")

def _default_downloads() -> str:
    home = _user_home()
    dl= os.path.join(home, "Downloads")
    return dl if os.path.isdir(dl) else home

def get_default_config_path() -> str:
    """ Gives the default path for the configuration file."""
    sys = platform.system().lower()
    if "windows" in sys:
        base = os.environ.get("APPDATA") or os.path.join(_user_home(), "AppData", "Roaming")
        cfg_dir = os.path.join(base, "FileFlow")
    elif "darwin" in sys or "mac" in sys:
        cfg_dir = os.path.join(_user_home(), "Library", "Application Support", "FileFlow")
    else:
        cfg_dir = os.path.join(_user_home(), ".config", "FileFlow")
    return os.path.join(cfg_dir, "config.json")

def parent_dir(path: str) -> str:
    parent = os.path.dirname(path)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)


def get_default_config() -> Dict[str, Any]:
    return {
        "version": 1,
        "include_paths": [_default_downloads()],
        "exclude_globs": ["*.partial", "*.tmp", "*.bak", "*.swp", "node_modules", ".git", "dist", "build", "pycache", "__pycache__", "Thumbs.db", ".DS_Store", "*.log", "*.cache", ".*"],
        "custom_rules": [
            {
                "name": "Music",
                "extensions": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"],
                "destination": "Music",
            }
            , {
                "name": "Pictures",
                "extensions": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".svg"],
            },
        ],
        "behavior": {
            "move": True,
            "conflict_policy": "skip",
            "sort_subfolders": True
        },
        "ui": { 
            "preview_window_limit":1000,
            "show_hidden_files": False,
            "show_system_files": False,
            "show_file_icons": True,
            "show_file_sizes": True,
        }
    }


def _is_str_list(val: Any) -> bool:
    return isinstance(val, list) and all(isinstance(x, str) for x in val)


def validate_config(cfg: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if not isinstance(cfg.get("version"), int):
        errors.append("version should be an integer")
    if isinstance(beh, dict):
        mv = beh.get("move")
        cp = beh.get("conflict_policy")
        if not isinstance(mv, bool):
            errors.append("behavior.move should be a boolean")
        if cp not in {"skip", "suffix"}:
            errors.append("behavior.conflict_policy should be 'skip' or 'suffix'")


    inc = cfg.get("include_paths")
    if not _is_str_list(inc) or not inc:
        errors.append("include_paths should not be non_empty")
    else:
        pass

    ex = cfg.get("exclude_globs")
    if not _is_str_list(ex):
        errors.append("exclude_globs should be a list of strings")

    rules = cfg.get("custom_rules")
    if not isinstance(rules, list):
        errors.append("custom_rules should be a list")
    else:
        for i, r in enumerate(rules):
            if not isinstance(r, dict):
                errors.append(f"custom_rules[{i}] should be a dict")
                continue
            name = r.get("name")
            exts = r.get("extensions")
            dest = r.get("destination")
            if not isinstance(name, str) or not name.strip():
                errors.append(f"custom_rules[{i}].name should be a string")
            if not _is_str_list(exts):
                errors.append(f"custom_rules[{i}].extensions should be a list of strings")
            else:
                for e in exts:
                    if not e.startswith("."):
                        errors.append(f"custom_rules[{i}].extensions should start with a dot: {e}")
            if not isinstance(dest, str) or not dest.strip():
                errors.append(f"custom_rules[{i}].destination should be a non-empty string")

    beh = cfg.get("behavior")
    if not isinstance(beh, dict):
        errors.append("behavior should be a object")
    else:
        mv = beh.get("move")
        cp = beh.get("conflict_policy")
        if not isinstance(mv, bool):
            errors.append("behavior.move should be a boolean")
        if cp not in {"skip","suffix"}:
            errors.append("behavior.conflict_policy should be 'skip' or 'suffix'") # more polcies complex later

    ui = cfg.get("ui")
    if not isinstance(ui, dict):
        errors.append("ui should be an object")
    else:
        limit = ui.get("preview_window_limit")
        sh = ui.get("show_hidden_files")
        if not isinstance(limit, int) or not (100 <= limit <= 10000):
            errors.append("ui.preview_window_limit should be an integer between 100 and 10000")
        if not isinstance(sh, bool):
            errors.append("ui.show_hidden_files should be a boolean")
    
    return (len(errors) == 0, errors)


def _deep_merge_defaults(defaults: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in defaults.items():
        if k in loaded:
            lv = loaded[k]
            if isinstance(v, dict) and isinstance(lv, dict):
                out[k] = _deep_merge_defaults(v, lv)
            else:
                out[k] = lv
        else:
            out[k] = v
    # Bring over any extra keys present in loaded that arent in defaults
    for k, v in loaded.items():
        if k not in out:
            out[k] = v
    return out

def load_config(path:str | None = None) -> Dict[str, Any]:
    defaults = get_default_config()
    if path is None:
        path = get_default_config_path()
    
    if not os.path.isfile(path):
        return defaults
    
    try: 
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        merged = _deep_merge_defaults(defaults, loaded)
        inc = merged.get("include_paths", [])
        dr = list(merged.get("destination_roots", []))
        if len(dr) < len(inc):
            dr += [""] * (len(inc) - len(dr))
        elif len(dr) > len(inc):
            dr = dr[:len(inc)]
        merged["destination_roots"] = dr
        ok, errs = validate_config(merged)
        if not ok:
            return defaults #resets to default settings boop
        return merged
    except Exception:
        return defaults #resets to default settings boop

def save_config(cfg: Dict[str, Any], path: str | None = None) -> None:
    if path is None:
        path = get_default_config_path()
    parent_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def resolve_destination_for_extension(ext: str, cfg: Dict[str, Any]) -> str:
    # Normalize incoming ext
    if not ext:
        return CATEGORY_DESTINATION_DEFAULT["Other"]
    e = ext.lower().strip()
    if not e.startswith('.'):
        e = '.' + e
    rules_map = cfg.get("rules", {}) or {}
    # Normalize keys in one pass so both "jpg" and ".jpg" work
    norm_rules = {}
    for k, v in rules_map.items():
        kk = k.strip().lower()
        if not kk.startswith('.'):
            kk = '.' + kk
        norm_rules[kk] = (v or "").strip()
    if e in norm_rules and norm_rules[e]:
        return norm_rules[e]
    custom_rules = cfg.get("custom_rules", []) or []
    for r in custom_rules:
        exts = r.get("extensions") or []
        dest = (r.get("destination") or "").strip()
        # Normalize list elements
        for x in exts:
            xx = x.lower().strip()
            if not xx.startswith('.'):
                xx = '.' + xx
            if e == xx and dest:
                return dest

    # Fallback to category mapping
    cat = infer_category(e)
    return CATEGORY_DESTINATION_DEFAULT.get(cat, CATEGORY_DESTINATION_DEFAULT["Other"])
