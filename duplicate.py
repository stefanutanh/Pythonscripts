import argparse
import hashlib
from collections import defaultdict
from pathlib import Path
import shutil


def get_file_hash(filepath: Path, chunk_size: int = 65536) -> str:
    """Beräknar SHA-256 i block för att inte överbelasta RAM vid stora filer."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(target_dir: Path) -> dict[str, list[Path]]:
    """Hittar dubletter effektivt: först storleksgruppering, därefter hash."""
    size_map = defaultdict(list)
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic"}

    # Steg 1: Samla filer och filtrera efter storlek
    for path in target_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in image_extensions:
            try:
                size_map[path.stat().st_size].append(path)
            except (PermissionError, FileNotFoundError):
                continue

    # Steg 2: Hasha bara filer som delar exakt samma filstorlek
    duplicates = defaultdict(list)
    for size, paths in size_map.items():
        if len(paths) > 1:
            for path in paths:
                try:
                    file_hash = get_file_hash(path)
                    duplicates[file_hash].append(path)
                except (PermissionError, FileNotFoundError):
                    continue

    # Returnera bara grupper med fler än 1 fil
    return {h: p for h, p in duplicates.items() if len(p) > 1}




if __name__ == "__main__":
    main()
