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


def get_safe_destination(quarantine_dir: Path, source_file: Path) -> Path:
    """Undviker att skriva över filer med samma namn i karantänmappen."""
    dest = quarantine_dir / source_file.name
    counter = 1
    while dest.exists():
        stem = source_file.stem
        suffix = source_file.suffix
        dest = quarantine_dir / f"{stem}_dup{counter}{suffix}"
        counter += 1
    return dest


def move_duplicates(duplicates: dict[str, list[Path]], quarantine_dir: Path):
    """Flyttar alla kopior utom den första (originalet) till karantän."""
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    moved_count = 0

    for file_hash, paths in duplicates.items():
        # Behåll första filen som original, flytta resten
        original = paths[0]
        copies = paths[1:]

        for copy_path in copies:
            dest = get_safe_destination(quarantine_dir, copy_path)
            try:
                shutil.move(str(copy_path), str(dest))
                print(f"Flyttad: {copy_path} -> {dest}")
                moved_count += 1
            except Exception as e:
                print(f"Fel vid flytt av {copy_path}: {e}")

    print(f"\nKlart! {moved_count} dubletter flyttades till: {quarantine_dir.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="Hitta och isolera bilddubletter säkert.")
    parser.add_argument("folder", type=str, help="Sökväg till mappen som ska scannas")
    parser.add_argument("--quarantine-dir", type=str, default="_karantan_dubletter", help="Namn på karantänmappen")
    args = parser.parse_args()

    target_path = Path(args.folder).resolve()
    quarantine_path = target_path / args.quarantine_dir

    if not target_path.exists() or not target_path.is_dir():
        print("Ogiltig sökväg.")
        return

    print(f"Scannar: {target_path} ...")
    duplicates = find_duplicates(target_path)

    if not duplicates:
        print("Inga dubletter hittades.")
        return

    total_copies = sum(len(paths) - 1 for paths in duplicates.values())
    print(f"\nHittade {len(duplicates)} grupper av dubletter ({total_copies} filer kan rensas):\n")

    for i, (file_hash, paths) in enumerate(duplicates.items(), 1):
        print(f"Grupp {i} (Original: {paths[0]}):")
        for copy_path in paths[1:]:
            print(f"  └── Dublett: {copy_path}")
        print()

    # Säkerhetsfråga före någon fil flyttas
    confirm = input("Vill du flytta dubletterna till karantänmappen? (j/N): ").strip().lower()
    if confirm in ("j", "ja", "y", "yes"):
        move_duplicates(duplicates, quarantine_path)
    else:
        print("Inga ändringar gjordes.")


if __name__ == "__main__":
    main()
