"""Punto de entrada: python run.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from entrenador.ui_app import App  # noqa: E402

if __name__ == "__main__":
    App().mainloop()
