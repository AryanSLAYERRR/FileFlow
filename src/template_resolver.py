import os
import time

def _date_parts(path: str):
    try:
        ts = os.stat(path).st_mtime
    except Exception:
        ts = time.time()
    t = time.localtime(ts)
    return {
        "yyyy": f"{t.tm_year:04d}",
        "mm": f"{t.tm_mon:02d}",
        "dd": f"{t.tm_mday:02d}",
    }

def apply_template(category: str, src_path: str, templates: dict[str, str] | None) -> str | None:
    if not templates:
        return None
    tpl = (templates or {}).get(category or "")
    if not tpl:
        return None
    parts = _date_parts(src_path)
    rel = tpl
    for k, v in parts.items():
        rel = rel.replace("{" + k + "}", v)
        return rel.strip().lstrip(os.sep).rstrip(os.sep)
        

    templates = cfg.get("templates", {})
    try:
        from src.template_resolver import apply_template
        subrel = apply_template(dest_folder_name, src_path, templates)
    except Exception:
        subrel = None

    if subrel:
        # subrel may already include top category (e.g., 'Images/2025/08')
        # If user put only '2025/08', we ensure the category root exists by prefixing
        if not subrel.lower().startswith(dest_folder_name.lower()):
            dest_rel = os.path.join(dest_folder_name, subrel)
        else:
            dest_rel = subrel
    else:
        dest_rel = dest_folder_name


