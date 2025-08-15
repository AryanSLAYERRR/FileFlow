
FILE_TYPES = {
    
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images",
    ".webp": "Images", ".bmp": "Images", ".tiff": "Images", ".svg": "Images",

    ".pdf": "Docs", ".doc": "Docs", ".docx": "Docs", ".xls": "Docs",
    ".xlsx": "Docs", ".ppt": "Docs", ".pptx": "Docs", ".txt": "Docs",
    ".md": "Docs", ".csv": "Docs", ".rtf": "Docs", ".odt": "Docs",

    ".mp4": "Videos", ".avi": "Videos", ".mov": "Videos",
    ".mkv": "Videos", ".flv": "Videos", ".wmv": "Videos", ".webm": "Videos",

    ".mp3": "Audio", ".wav": "Audio", ".aac": "Audio",
    ".flac": "Audio", ".ogg": "Audio", ".m4a": "Audio", ".wma": "Audio",

    ".zip": "Archives", ".rar": "Archives", ".tar": "Archives",
    ".gz": "Archives", ".7z": "Archives", ".bz2": "Archives",

    ".py": "Code", ".js": "Code", ".java": "Code",
    ".c": "Code", ".cpp": "Code", ".cs": "Code", ".go": "Code",
    ".php": "Code", ".rb": "Code", ".html": "Code", ".css": "Code",
    ".sh": "Code", ".sql": "Code", ".json": "Code", ".xml": "Code",
    ".yaml": "Code", ".yml": "Code", ".rs": "Code",
    ".swift": "Code", ".kt": "Code", ".pl": "Code", ".lua": "Code",
    ".dart": "Code", ".ts": "Code", ".tsx": "Code", ".jsx": "Code",
    ".asm": "Code", ".h": "Code", ".hpp": "Code", ".m": "Code",
}

CATEGORY_DESTINATION_DEFAULT = {
    "Images": "Images",
    "Docs": "Docs", 
    "Videos": "Videos",
    "Audio": "Audio",
    "Archives": "Archives",
    "Code": "Code",
    "Other": "other",
}

def infer_category(ext: str) -> str:
    """Return a broad category for the given file extension.
    If the extension is not recognized, return 'Other'."""
    if not ext:
        return "Other"
    ext = ext.lower().strip()
    if not ext.startswith('.'):
        ext = '.' + ext
    return FILE_TYPES.get(ext, "Other")