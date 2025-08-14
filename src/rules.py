from typing import Dict
from .config import resolve_destination_for_extension

def resolve_for_file(ext: str, cfg: Dict) -> str:
    return resolve_destination_for_extension(ext, cfg)