from pathlib import Path
from typing import Union
from app.core.config import settings


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensures directory exists and returns Path object."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def is_safe_path(base_directory: Union[str, Path], target_file: Union[str, Path]) -> bool:
    """Verifies that target_file resolves within base_directory to prevent Path Traversal attacks."""
    try:
        base = Path(base_directory).resolve()
        target = Path(target_file).resolve()
        return base in target.parents or base == target
    except Exception:
        return False
