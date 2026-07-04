"""Construit l'exécutable du jeu pour le système courant.

    python build.py

Produit `dist/Nim.exe` (Windows), `dist/Nim.app` (macOS) ou `dist/Nim` (Linux).
Nécessite PyInstaller :  pip install pyinstaller
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).parent
ENTREE = RACINE / "sources" / "jeu_nim.py"

ICONES = {
    "win32": RACINE / "assets" / "icon.ico",
    "darwin": RACINE / "assets" / "icon.icns",
}


def main() -> int:
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean", "--windowed", "--onefile",
        "--name", "Nim",
        "--paths", str(RACINE / "sources"),
    ]
    icone = ICONES.get(sys.platform)
    if icone and icone.exists():
        cmd += ["--icon", str(icone)]
    cmd.append(str(ENTREE))

    print(" ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
