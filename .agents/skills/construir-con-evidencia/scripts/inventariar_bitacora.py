#!/usr/bin/env python3
"""Inventariar Markdown numerado en una bitácora o carpeta documental."""

import argparse
import json
import os
import re
from pathlib import Path


NUMBERED = re.compile(r"^(\d+(?:\.\d+)*)([ _-]+)(.+)\.md$", re.IGNORECASE)
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[ _.-]|$)")
IGNORED = {".git", "node_modules", ".venv", "__pycache__"}


def summarize(directory, root, exists=True):
    entries = []
    unsequenced = []
    warnings = []
    skipped_links = []
    widths = []
    separators = set()
    for file in sorted(directory.iterdir()) if exists else []:
        if file.is_symlink():
            skipped_links.append(file.name)
            continue
        if not file.is_file() or file.suffix.lower() != ".md":
            continue
        match = NUMBERED.fullmatch(file.name)
        if match and not ISO_DATE.match(file.name):
            digits, separator, _title = match.groups()
            parts = tuple(int(part) for part in digits.split("."))
            number = parts[0] if len(parts) == 1 else ".".join(map(str, parts))
            entries.append(
                {
                    "number": number,
                    "file": file.name,
                    "_parts": parts,
                }
            )
            widths.append(len(digits.split(".", 1)[0]))
            separators.add(separator)
        else:
            unsequenced.append(file.name)
            if file.name[0].isdigit():
                warnings.append(f"Convención numérica sin resolver: {file.name}")
    entries.sort(key=lambda entry: (entry["_parts"], entry["file"]))
    grouped = {}
    for entry in entries:
        grouped.setdefault(entry["_parts"], []).append(entry["file"])
    duplicates = [
        {
            "number": number[0]
            if len(number) == 1
            else ".".join(map(str, number)),
            "files": files,
        }
        for number, files in grouped.items()
        if len(files) > 1
    ]
    if duplicates:
        warnings.append("Hay números duplicados; revisar la carpeta antes de escribir.")
    next_number = max((number[0] for number in grouped), default=0) + 1
    width = max(widths, default=2)
    public_entries = [
        {key: value for key, value in entry.items() if key != "_parts"}
        for entry in entries
    ]
    return {
        "directory": directory.relative_to(root).as_posix(),
        "exists": exists,
        "entries": public_entries,
        "unsequenced_markdown": unsequenced,
        "duplicates": duplicates,
        "next_prefix": None if warnings else str(next_number).zfill(width),
        "separators": sorted(separators),
        "warnings": warnings,
        "skipped_symlinks": skipped_links,
    }


def inventory(root, selected=None):
    root = Path(root).expanduser().absolute()
    if root.is_symlink():
        raise ValueError("La raíz es un enlace simbólico; indicar su destino revisado.")
    root = root.resolve()
    if root.exists() and not root.is_dir():
        raise ValueError("La raíz debe ser un directorio.")
    chosen = None
    if selected is not None:
        relative = Path(selected)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("--carpeta debe ser relativa a la bitácora y sin '..'.")
        chosen = root / relative
        cursor = root
        for part in relative.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise ValueError("La carpeta seleccionada contiene un enlace simbólico.")
        if chosen.exists() and not chosen.is_dir():
            raise ValueError("La carpeta seleccionada no es un directorio.")
    directories = []
    skipped = []

    def fail_on_error(error):
        raise error

    if root.exists():
        for current, children, _files in os.walk(
            root, followlinks=False, onerror=fail_on_error
        ):
            directory = Path(current)
            accepted = []
            for child in sorted(children):
                path = directory / child
                if child in IGNORED or path.is_symlink():
                    skipped.append(path.relative_to(root).as_posix())
                else:
                    accepted.append(child)
            children[:] = accepted
            directories.append(summarize(directory, root))
    else:
        directories.append(summarize(root, root, exists=False))
    selection = None
    if chosen is not None:
        selection = summarize(chosen, root, exists=chosen.exists())
    return {
        "root": str(root),
        "exists": root.exists(),
        "directories": directories,
        "selected": selection,
        "skipped_directories": skipped,
        "read_only": True,
        "note": "Sugerencias sin reserva; releer antes de escribir y respetar el estilo local.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="Raíz documental ya localizada")
    parser.add_argument("--carpeta", help="Subcarpeta elegida; '.' para la raíz")
    args = parser.parse_args()
    try:
        result = inventory(args.root, args.carpeta)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
