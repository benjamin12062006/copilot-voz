#!/usr/bin/env python3
"""Crear la estructura documental mínima de construir-con-evidencia."""

import argparse
import json
from pathlib import Path


def relative_path(value, option):
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{option} debe ser una ruta relativa sin '..'.")
    return path


def ensure_directory(path):
    if path.exists() and not path.is_dir():
        raise ValueError(f"La ruta existe y no es un directorio: {path}")
    path.mkdir(parents=True, exist_ok=True)


def initialize(root, bitacora, docs):
    root = Path(root).expanduser().absolute()
    if root.is_symlink():
        raise ValueError("La raíz es un enlace simbólico; indicar su destino revisado.")
    root = root.resolve()
    if not root.is_dir():
        raise ValueError("La raíz del proyecto debe existir y ser un directorio.")

    bitacora_path = root / relative_path(bitacora, "--bitacora")
    docs_path = root / relative_path(docs, "--docs")
    targets = [bitacora_path, docs_path / "fonts", docs_path / "plans"]
    for target in targets:
        ensure_directory(target)

    return {
        "root": str(root),
        "directories": [str(path.relative_to(root)) for path in targets],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="Raíz existente del proyecto o componente")
    parser.add_argument("--bitacora", default="bitacora-construccion")
    parser.add_argument("--docs", default="docs")
    args = parser.parse_args()
    try:
        result = initialize(args.root, args.bitacora, args.docs)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
